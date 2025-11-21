"""
CodeLoader 单元测试

测试代码仓库加载服务的功能：
- 本地仓库文件遍历
- 文件过滤（扩展名、大小、忽略目录）
- 语言检测
- 错误处理
"""

import os
from pathlib import Path

import pytest

from app.core.exceptions import AgentException, AgentErrorCode
from app.services.code_loader import CodeLoader, detect_language, IGNORED_DIRS, SUPPORTED_EXTENSIONS


class TestDetectLanguage:
    """测试语言检测函数"""

    def test_java_detection(self):
        """测试 Java 文件检测"""
        assert detect_language(Path("User.java")) == "java"
        assert detect_language(Path("src/main/java/User.java")) == "java"

    def test_python_detection(self):
        """测试 Python 文件检测"""
        assert detect_language(Path("main.py")) == "python"
        assert detect_language(Path("app/services/auth.py")) == "python"

    def test_typescript_detection(self):
        """测试 TypeScript 文件检测"""
        assert detect_language(Path("App.tsx")) == "typescript"
        assert detect_language(Path("utils.ts")) == "typescript"

    def test_javascript_detection(self):
        """测试 JavaScript 文件检测"""
        assert detect_language(Path("index.js")) == "javascript"
        assert detect_language(Path("Button.jsx")) == "javascript"

    def test_markdown_detection(self):
        """测试 Markdown 文件检测"""
        assert detect_language(Path("README.md")) == "markdown"

    def test_unknown_extension(self):
        """测试未知扩展名（应返回 'text'）"""
        assert detect_language(Path("config.xml")) == "text"
        assert detect_language(Path("data.csv")) == "text"

    def test_case_insensitive(self):
        """测试扩展名大小写不敏感"""
        assert detect_language(Path("User.JAVA")) == "java"
        assert detect_language(Path("Main.PY")) == "python"


class TestCodeLoader:
    """CodeLoader 测试套件"""

    def test_load_sample_repository(self, sample_repository_path: Path):
        """测试加载示例仓库"""
        loader = CodeLoader(max_file_size=1024 * 1024)  # 1MB
        code_files = loader.load_repository(project_id=1, repo_path=str(sample_repository_path))

        # 验证基本断言
        assert len(code_files) > 0, "应该加载至少一个文件"

        # 验证 CodeFile 结构
        for code_file in code_files:
            assert code_file.project_id == 1
            assert code_file.path, "路径不应为空"
            assert code_file.language, "语言不应为空"
            assert code_file.content, "内容不应为空"
            assert code_file.size_bytes > 0, "文件大小应 > 0"

    def test_supported_extensions_filter(self, tmp_path: Path):
        """测试支持的文件扩展名过滤"""
        # 创建测试文件
        (tmp_path / "User.java").write_text("public class User {}")
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "data.txt").write_text("some text")  # 不支持的扩展名
        (tmp_path / "binary.exe").write_bytes(b"\x00\x01\x02")  # 不支持

        loader = CodeLoader(max_file_size=1024 * 1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        # 应该只加载支持的文件
        loaded_paths = {f.path for f in code_files}
        assert "User.java" in loaded_paths
        assert "main.py" in loaded_paths
        assert "README.md" in loaded_paths
        assert "data.txt" not in loaded_paths
        assert "binary.exe" not in loaded_paths

    def test_ignored_directories_filter(self, tmp_path: Path):
        """测试忽略目录过滤"""
        # 创建正常目录
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "Main.java").write_text("public class Main {}")

        # 创建忽略目录
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")

        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.json").write_text("{}")

        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "cache.py").write_text("# cache")

        loader = CodeLoader(max_file_size=1024 * 1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        # 验证只加载了 src 目录的文件
        loaded_paths = {f.path for f in code_files}
        assert "src/Main.java" in loaded_paths
        assert not any(".git" in path for path in loaded_paths)
        assert not any("node_modules" in path for path in loaded_paths)
        assert not any("__pycache__" in path for path in loaded_paths)

    def test_max_file_size_limit(self, tmp_path: Path):
        """测试文件大小限制"""
        # 创建小文件
        small_file = tmp_path / "Small.java"
        small_file.write_text("public class Small {}")

        # 创建大文件（超过限制）
        large_file = tmp_path / "Large.java"
        large_content = "// " + ("x" * 2000)  # 约 2KB
        large_file.write_text(large_content)

        # 设置 1KB 的限制
        loader = CodeLoader(max_file_size=1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        # 应该只加载小文件
        loaded_paths = {f.path for f in code_files}
        assert "Small.java" in loaded_paths
        assert "Large.java" not in loaded_paths

    def test_relative_path_calculation(self, tmp_path: Path):
        """测试相对路径计算的正确性"""
        # 创建嵌套目录
        nested_dir = tmp_path / "src" / "main" / "java" / "com" / "example"
        nested_dir.mkdir(parents=True)
        (nested_dir / "User.java").write_text("public class User {}")

        loader = CodeLoader(max_file_size=1024 * 1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        # 验证相对路径使用正斜杠
        assert len(code_files) == 1
        assert code_files[0].path == "src/main/java/com/example/User.java"

    def test_nonexistent_path_error(self):
        """测试不存在的路径应抛出异常"""
        loader = CodeLoader(max_file_size=1024 * 1024)

        with pytest.raises(AgentException) as exc_info:
            loader.load_repository(project_id=1, repo_path="/nonexistent/path/to/repo")

        assert exc_info.value.error_code == AgentErrorCode.REPOSITORY_ERROR

    def test_file_path_as_repo_error(self, tmp_path: Path):
        """测试传入文件路径（而非目录）应抛出异常"""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        loader = CodeLoader(max_file_size=1024 * 1024)

        with pytest.raises(AgentException) as exc_info:
            loader.load_repository(project_id=1, repo_path=str(file_path))

        assert exc_info.value.error_code == AgentErrorCode.REPOSITORY_ERROR

    def test_utf8_encoding_handling(self, tmp_path: Path):
        """测试 UTF-8 编码文件的正确处理"""
        # 创建包含中文的文件
        chinese_file = tmp_path / "Chinese.java"
        chinese_file.write_text("public class 用户 { // 中文注释 }", encoding="utf-8")

        loader = CodeLoader(max_file_size=1024 * 1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        assert len(code_files) == 1
        assert "用户" in code_files[0].content
        assert "中文注释" in code_files[0].content

    def test_multiple_projects_different_ids(self, tmp_path: Path):
        """测试不同项目 ID 的文件隔离"""
        (tmp_path / "File1.java").write_text("class File1 {}")

        loader = CodeLoader(max_file_size=1024 * 1024)

        files_proj1 = loader.load_repository(project_id=1, repo_path=str(tmp_path))
        files_proj2 = loader.load_repository(project_id=2, repo_path=str(tmp_path))

        # 相同路径，不同项目 ID
        assert files_proj1[0].project_id == 1
        assert files_proj2[0].project_id == 2

    def test_language_detection_integration(self, tmp_path: Path):
        """测试语言检测集成到加载流程"""
        (tmp_path / "App.tsx").write_text("export const App = () => {}")
        (tmp_path / "utils.js").write_text("function utils() {}")
        (tmp_path / "service.py").write_text("def service(): pass")

        loader = CodeLoader(max_file_size=1024 * 1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        # 验证语言检测
        languages = {f.path: f.language for f in code_files}
        assert languages["App.tsx"] == "typescript"
        assert languages["utils.js"] == "javascript"
        assert languages["service.py"] == "python"

    def test_empty_repository(self, tmp_path: Path):
        """测试空仓库（无有效文件）"""
        # 创建空目录
        (tmp_path / "empty").mkdir()

        loader = CodeLoader(max_file_size=1024 * 1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        # 空仓库应返回空列表
        assert len(code_files) == 0

    def test_mixed_line_endings(self, tmp_path: Path):
        """测试混合换行符的文件（Windows/Unix）"""
        mixed_file = tmp_path / "Mixed.java"
        # Windows 风格 \r\n 和 Unix 风格 \n
        content = "public class Mixed {\r\n    // Windows line\n    // Unix line\r\n}"
        mixed_file.write_text(content, encoding="utf-8")

        loader = CodeLoader(max_file_size=1024 * 1024)
        code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

        assert len(code_files) == 1
        # Python 会自动规范化换行符
        assert "Windows line" in code_files[0].content
        assert "Unix line" in code_files[0].content

    def test_symlink_handling(self, tmp_path: Path):
        """测试符号链接的处理（如果操作系统支持）"""
        # 创建真实文件
        real_file = tmp_path / "Real.java"
        real_file.write_text("public class Real {}")

        # 尝试创建符号链接（可能在 Windows 上失败）
        try:
            link_file = tmp_path / "Link.java"
            link_file.symlink_to(real_file)

            loader = CodeLoader(max_file_size=1024 * 1024)
            code_files = loader.load_repository(project_id=1, repo_path=str(tmp_path))

            # 验证符号链接被正确处理
            loaded_paths = {f.path for f in code_files}
            assert "Real.java" in loaded_paths

        except OSError:
            # 符号链接不支持（如 Windows 无管理员权限）
            pytest.skip("符号链接不被当前环境支持")

    def test_supported_extensions_constant(self):
        """验证 SUPPORTED_EXTENSIONS 常量"""
        assert ".java" in SUPPORTED_EXTENSIONS
        assert ".py" in SUPPORTED_EXTENSIONS
        assert ".ts" in SUPPORTED_EXTENSIONS
        assert ".tsx" in SUPPORTED_EXTENSIONS
        assert ".js" in SUPPORTED_EXTENSIONS
        assert ".jsx" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS
        assert ".yml" in SUPPORTED_EXTENSIONS
        assert ".yaml" in SUPPORTED_EXTENSIONS
        assert ".json" in SUPPORTED_EXTENSIONS

    def test_ignored_dirs_constant(self):
        """验证 IGNORED_DIRS 常量"""
        assert ".git" in IGNORED_DIRS
        assert ".idea" in IGNORED_DIRS
        assert ".vscode" in IGNORED_DIRS
        assert "node_modules" in IGNORED_DIRS
        assert "dist" in IGNORED_DIRS
        assert "build" in IGNORED_DIRS
        assert "__pycache__" in IGNORED_DIRS
        assert ".venv" in IGNORED_DIRS
        assert "venv" in IGNORED_DIRS
