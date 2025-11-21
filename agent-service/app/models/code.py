"""
代码相关内部模型。

这些模型用于代码加载、分块与向量化过程，不直接对外暴露为 API。
"""

from dataclasses import dataclass

from langchain_core.documents import Document


@dataclass
class CodeFile:
    """表示单个源代码文件。"""

    project_id: int
    path: str
    language: str
    content: str
    size_bytes: int


@dataclass
class CodeChunk:
    """表示分块后的代码片段。"""

    id: str
    project_id: int
    path: str
    language: str
    content: str
    start_line: int
    end_line: int

    def to_document(self) -> Document:
        """
        转换为 LangChain Document，用于向量索引与检索。
        """
        metadata = {
            "project_id": self.project_id,
            "path": self.path,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
        }
        return Document(page_content=self.content, metadata=metadata)

