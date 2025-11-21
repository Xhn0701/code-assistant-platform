"""
CodeSplitter 单元测试

测试代码分块服务的核心功能：
- 代码文件分块
- 行号估算
- 元数据传递
"""

import pytest

from app.models.code import CodeChunk, CodeFile
from app.services.code_splitter import CodeSplitter


class TestCodeSplitter:
    """CodeSplitter 测试套件"""

    def test_split_basic_functionality(self, sample_java_code_file: CodeFile):
        """测试基本分块功能"""
        splitter = CodeSplitter(chunk_size=200, chunk_overlap=50)
        chunks = splitter.split_code_file(sample_java_code_file)

        # 验证基本断言
        assert len(chunks) > 0, "应该生成至少一个代码块"
        assert all(isinstance(chunk, CodeChunk) for chunk in chunks), "所有元素应为 CodeChunk"

    def test_chunk_metadata_consistency(self, sample_java_code_file: CodeFile):
        """测试代码块元数据一致性"""
        splitter = CodeSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_code_file(sample_java_code_file)

        for chunk in chunks:
            # 验证元数据一致性
            assert chunk.project_id == sample_java_code_file.project_id, "projectId 应一致"
            assert chunk.path == sample_java_code_file.path, "路径应一致"
            assert chunk.language == sample_java_code_file.language, "语言应一致"

            # 验证内容不为空
            assert chunk.content.strip(), "代码块内容不应为空"

            # 验证 ID 格式
            assert chunk.id.startswith(sample_java_code_file.path), "ID 应包含文件路径"

    def test_line_numbers_are_sequential(self, sample_long_code_file: CodeFile):
        """测试行号是否递增且连续"""
        splitter = CodeSplitter(chunk_size=300, chunk_overlap=50)
        chunks = splitter.split_code_file(sample_long_code_file)

        # 验证行号递增
        for i in range(len(chunks) - 1):
            assert chunks[i].start_line > 0, "起始行号应从 1 开始"
            assert chunks[i].end_line >= chunks[i].start_line, "结束行号应 >= 起始行号"

            # 下一个块的起始行应该 > 当前块的结束行
            assert (
                chunks[i + 1].start_line > chunks[i].end_line
            ), f"行号应递增: chunk[{i}].end={chunks[i].end_line}, chunk[{i+1}].start={chunks[i+1].start_line}"

    def test_approximate_line_numbers(self, sample_java_code_file: CodeFile):
        """测试近似行号计算的准确性"""
        splitter = CodeSplitter(chunk_size=2000, chunk_overlap=0)  # 足够大，保证只有一个块
        chunks = splitter.split_code_file(sample_java_code_file)

        # 单个块应包含整个文件
        assert len(chunks) == 1, "大 chunk_size 应只生成一个块"

        chunk = chunks[0]

        # 计算实际行数
        actual_lines = sample_java_code_file.content.count("\n")

        # 允许 ±5 行的误差（由于近似算法）
        assert abs(chunk.end_line - actual_lines) <= 5, (
            f"行号估算误差过大: 实际 {actual_lines} 行，"
            f"估算 {chunk.start_line}-{chunk.end_line}"
        )

    def test_chunk_size_parameter_affects_result(self, sample_long_code_file: CodeFile):
        """测试 chunk_size 参数对分块数量的影响"""
        small_splitter = CodeSplitter(chunk_size=200, chunk_overlap=0)
        large_splitter = CodeSplitter(chunk_size=1000, chunk_overlap=0)

        small_chunks = small_splitter.split_code_file(sample_long_code_file)
        large_chunks = large_splitter.split_code_file(sample_long_code_file)

        # 更小的 chunk_size 应产生更多的代码块
        assert len(small_chunks) > len(large_chunks), (
            f"小 chunk_size 应产生更多块: "
            f"200={len(small_chunks)}, 1000={len(large_chunks)}"
        )

    def test_chunk_overlap_affects_content(self, sample_java_code_file: CodeFile):
        """测试 chunk_overlap 参数的效果"""
        no_overlap = CodeSplitter(chunk_size=300, chunk_overlap=0)
        with_overlap = CodeSplitter(chunk_size=300, chunk_overlap=50)

        chunks_no_overlap = no_overlap.split_code_file(sample_java_code_file)
        chunks_with_overlap = with_overlap.split_code_file(sample_java_code_file)

        # 有重叠的分块可能会产生更多块（因为每块实际内容较少）
        # 但至少应该有相同或更多的块
        assert len(chunks_with_overlap) >= len(chunks_no_overlap)

    def test_empty_file_handling(self):
        """测试空文件的处理"""
        empty_file = CodeFile(
            project_id=1,
            path="Empty.java",
            language="java",
            content="",
            size_bytes=0,
        )

        splitter = CodeSplitter(chunk_size=100, chunk_overlap=0)
        chunks = splitter.split_code_file(empty_file)

        # 空文件应该产生 0 或 1 个空块
        assert len(chunks) <= 1

        if len(chunks) == 1:
            assert chunks[0].content == ""

    def test_single_line_file(self):
        """测试单行文件的处理"""
        single_line_file = CodeFile(
            project_id=1,
            path="Single.java",
            language="java",
            content="public class Single {}",
            size_bytes=22,
        )

        splitter = CodeSplitter(chunk_size=100, chunk_overlap=0)
        chunks = splitter.split_code_file(single_line_file)

        assert len(chunks) == 1
        assert chunks[0].start_line == 1
        # 单行文件可能 end_line 为 1 或 2（取决于是否有尾随换行符）
        assert chunks[0].end_line <= 2

    def test_chunk_id_uniqueness(self, sample_java_code_file: CodeFile):
        """测试代码块 ID 的唯一性"""
        splitter = CodeSplitter(chunk_size=200, chunk_overlap=0)
        chunks = splitter.split_code_file(sample_java_code_file)

        chunk_ids = [chunk.id for chunk in chunks]

        # 验证 ID 唯一性
        assert len(chunk_ids) == len(set(chunk_ids)), "Chunk ID 应该唯一"

        # 验证 ID 格式（应包含索引）
        for i, chunk in enumerate(chunks):
            assert f"::{i}" in chunk.id, f"Chunk ID 应包含索引: {chunk.id}"

    def test_to_document_conversion(self, sample_java_code_file: CodeFile):
        """测试 CodeChunk.to_document() 转换"""
        splitter = CodeSplitter(chunk_size=500, chunk_overlap=0)
        chunks = splitter.split_code_file(sample_java_code_file)

        for chunk in chunks:
            doc = chunk.to_document()

            # 验证 LangChain Document 结构
            assert doc.page_content == chunk.content
            assert doc.metadata["project_id"] == chunk.project_id
            assert doc.metadata["path"] == chunk.path
            assert doc.metadata["language"] == chunk.language
            assert doc.metadata["start_line"] == chunk.start_line
            assert doc.metadata["end_line"] == chunk.end_line

    def test_large_file_splitting(self):
        """测试大文件的分块（模拟真实场景）"""
        # 创建一个包含 100 行代码的模拟文件
        lines = [f"    public void method{i}() {{\n        // Implementation\n    }}\n" for i in range(100)]
        large_content = "\n".join(lines)

        large_file = CodeFile(
            project_id=1,
            path="LargeService.java",
            language="java",
            content=large_content,
            size_bytes=len(large_content),
        )

        splitter = CodeSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_code_file(large_file)

        # 验证
        assert len(chunks) > 5, "大文件应分成多个块"

        # 验证覆盖完整性（第一块从第 1 行开始）
        assert chunks[0].start_line == 1

        # 验证最后一块的结束行号接近实际行数
        actual_lines = large_content.count("\n")
        assert chunks[-1].end_line >= actual_lines * 0.9  # 允许 10% 误差

    def test_different_languages(self, sample_python_code_file: CodeFile):
        """测试不同编程语言的代码分块"""
        splitter = CodeSplitter(chunk_size=300, chunk_overlap=50)

        # Python 文件
        python_chunks = splitter.split_code_file(sample_python_code_file)

        assert len(python_chunks) > 0
        assert all(chunk.language == "python" for chunk in python_chunks)

    def test_chunk_content_is_substring_of_original(self, sample_java_code_file: CodeFile):
        """验证每个代码块的内容都是原文件的子串"""
        splitter = CodeSplitter(chunk_size=300, chunk_overlap=50)
        chunks = splitter.split_code_file(sample_java_code_file)

        for chunk in chunks:
            # 每个块的内容应该在原文件中
            # 注意：由于 overlap，可能会有重复
            assert chunk.content in sample_java_code_file.content, (
                f"Chunk 内容应该是原文件的子串\n"
                f"Chunk: {chunk.content[:50]}..."
            )
