"""
代码仓库加载服务。

当前仅支持本地仓库路径，后续可以扩展 GitHub / 远程仓库。
"""

import logging
import os
from pathlib import Path
from typing import List

from app.core.exceptions import AgentErrorCode, AgentException
from app.models.code import CodeFile

logger = logging.getLogger(__name__)


IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
}

SUPPORTED_EXTENSIONS = {
    ".java",
    ".kt",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".md",
    ".yml",
    ".yaml",
    ".json",
}


def detect_language(path: Path) -> str:
    """根据文件扩展名推断语言（简单映射）。"""
    suffix = path.suffix.lower()
    if suffix in {".java"}:
        return "java"
    if suffix in {".ts", ".tsx"}:
        return "typescript"
    if suffix in {".js", ".jsx"}:
        return "javascript"
    if suffix in {".py"}:
        return "python"
    if suffix in {".md"}:
        return "markdown"
    return "text"


class CodeLoader:
    """从本地仓库加载代码文件。"""

    def __init__(self, max_file_size: int) -> None:
        self._max_file_size = max_file_size

    def load_repository(self, project_id: int, repo_path: str) -> List[CodeFile]:
        """
        加载仓库中的所有代码文件。

        Args:
            project_id: 项目 ID
            repo_path: 本地仓库路径
        """
        root = Path(repo_path).resolve()
        if not root.exists() or not root.is_dir():
            raise AgentException(
                AgentErrorCode.REPOSITORY_ERROR,
                f"仓库路径不存在或不是目录: {repo_path}",
            )

        code_files: List[CodeFile] = []

        for dirpath, dirnames, filenames in os.walk(root):
            # 过滤忽略目录
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

            for filename in filenames:
                path = Path(dirpath) / filename
                rel_path = path.relative_to(root)
                suffix = path.suffix.lower()

                if suffix not in SUPPORTED_EXTENSIONS:
                    continue

                try:
                    size = path.stat().st_size
                    if size > self._max_file_size:
                        logger.info(
                            "跳过过大文件: %s (size=%d)", rel_path.as_posix(), size
                        )
                        continue

                    content = path.read_text(encoding="utf-8", errors="ignore")
                except Exception as exc:
                    logger.error("读取文件失败: %s, 错误=%s", path, exc)
                    raise AgentException(
                        AgentErrorCode.REPOSITORY_ERROR,
                        "读取仓库文件失败",
                        data={"path": str(path), "error": str(exc)},
                    ) from exc

                code_files.append(
                    CodeFile(
                        project_id=project_id,
                        path=rel_path.as_posix(),
                        language=detect_language(path),
                        content=content,
                        size_bytes=size,
                    )
                )

        logger.info("仓库 %s 共加载 %d 个代码文件", root, len(code_files))
        return code_files


__all__ = ["CodeLoader"]

