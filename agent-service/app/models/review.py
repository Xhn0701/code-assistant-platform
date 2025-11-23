"""
Code Review 相关数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class StaticIssue:
    """静态分析发现的问题"""
    file_path: str
    line: int
    severity: str  # critical, warning, info
    category: str  # security, performance, style, complexity
    rule: str      # 规则名称
    message: str
    source: str = "static"  # 来源: static/llm


@dataclass
class Issue:
    """审查发现的问题 (统一格式)"""
    file_path: str
    line: int
    severity: str  # critical, warning, info
    category: str  # security, performance, design, practice
    message: str
    reason: str = ""       # 问题原因
    suggestion: str = ""   # 改进建议
    example: str = ""      # 示例代码
    evidence: str = ""     # 问题证据
    impact: str = ""       # 潜在影响
    source: str = "llm"    # 来源: static/llm


@dataclass
class ReviewReport:
    """审查报告"""
    project_id: int
    score: int  # 0-100
    level: str  # quick, standard, full
    total_files: int
    reviewed_files: int
    total_issues: int
    critical_count: int
    warning_count: int
    info_count: int
    issues_by_category: Dict[str, List[Issue]]
    top_issues: List[Issue] = field(default_factory=list)
    summary: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        """转换为字典"""
        return {
            "project_id": self.project_id,
            "score": self.score,
            "level": self.level,
            "total_files": self.total_files,
            "reviewed_files": self.reviewed_files,
            "total_issues": self.total_issues,
            "critical_count": self.critical_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "issues_by_category": {
                cat: [self._issue_to_dict(i) for i in issues]
                for cat, issues in self.issues_by_category.items()
            },
            "top_issues": [self._issue_to_dict(i) for i in self.top_issues],
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }

    def _issue_to_dict(self, issue: Issue) -> dict:
        """Issue转换为字典"""
        return {
            "file_path": issue.file_path,
            "line": issue.line,
            "severity": issue.severity,
            "category": issue.category,
            "message": issue.message,
            "reason": issue.reason,
            "suggestion": issue.suggestion,
            "example": issue.example,
            "evidence": issue.evidence,
            "impact": issue.impact,
            "source": issue.source
        }


@dataclass
class CodeFile:
    """代码文件信息"""
    path: str
    language: str
    content: str
    line_count: int = 0

    def __post_init__(self):
        if not self.line_count:
            self.line_count = len(self.content.split('\n'))
