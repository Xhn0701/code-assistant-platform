"""
代码分块服务。

当前使用 RecursiveCharacterTextSplitter 做近似分块，并根据换行数估算行号。
"""

import logging
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.models.code import CodeChunk, CodeFile

logger = logging.getLogger(__name__)


class CodeSplitter:
    """基于文本的代码分块服务（近似行号）。"""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=[
                "\n\n",
                "\n",
                "}",
                ";",
                " ",
            ],
        )

    def split_code_file(self, code_file: CodeFile) -> List[CodeChunk]:
        """
        将单个 CodeFile 分块，并估算每个块的起止行号。

        行号算法为近似：按 chunk 中的换行符计数，累加得到大致位置。
        对于后续基于 tree-sitter 的精确分块，会进行替换。
        """
        chunks = self._splitter.split_text(code_file.content)
        result: List[CodeChunk] = []
        current_line = 1

        for idx, chunk_text in enumerate(chunks):
            line_count = chunk_text.count("\n")
            start_line = current_line
            end_line = current_line + line_count

            chunk_id = f"{code_file.path}::{idx}"

            result.append(
                CodeChunk(
                    id=chunk_id,
                    project_id=code_file.project_id,
                    path=code_file.path,
                    language=code_file.language,
                    content=chunk_text,
                    start_line=start_line,
                    end_line=end_line,
                )
            )

            current_line = end_line + 1

        logger.debug(
            "文件 %s 分块完成：%d 块", code_file.path, len(result)
        )
        return result


__all__ = ["CodeSplitter"]

