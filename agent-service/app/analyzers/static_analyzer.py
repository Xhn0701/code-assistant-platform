"""
静态代码分析器
集成多个静态分析工具,统一输出格式
"""
import os
import re
import subprocess
import json
import logging
from typing import List, Dict
from pathlib import Path

from app.models.review import StaticIssue

logger = logging.getLogger(__name__)


class StaticAnalyzer:
    """统一的静态分析接口"""

    def __init__(self):
        self.analyzers = {
            'python': self._analyze_python,
            'javascript': self._analyze_javascript,
            'typescript': self._analyze_javascript,  # TypeScript使用ESLint
        }

    async def analyze_project(self, project_path: str) -> List[StaticIssue]:
        """
        分析整个项目

        Args:
            project_path: 项目根目录路径

        Returns:
            按严重程度排序的问题列表
        """
        logger.info(f"开始静态分析项目: {project_path}")
        issues = []

        # 1. 检测项目语言类型
        languages = self._detect_languages(project_path)
        logger.info(f"检测到的语言: {languages}")

        # 2. 执行对应的分析器
        for lang in languages:
            if analyzer := self.analyzers.get(lang):
                try:
                    lang_issues = await analyzer(project_path)
                    issues.extend(lang_issues)
                    logger.info(f"{lang} 分析完成,发现 {len(lang_issues)} 个问题")
                except Exception as e:
                    logger.error(f"{lang} 分析失败: {e}")

        # 3. 按严重程度排序
        issues.sort(key=lambda x: self._severity_weight(x.severity), reverse=True)

        logger.info(f"静态分析完成,共发现 {len(issues)} 个问题")
        return issues

    def _detect_languages(self, project_path: str) -> List[str]:
        """检测项目使用的编程语言"""
        languages = set()

        # 遍历项目文件,根据扩展名判断语言
        for root, _, files in os.walk(project_path):
            # 跳过常见的排除目录
            if any(skip in root for skip in ['node_modules', 'venv', '.git', '__pycache__', 'dist', 'build']):
                continue

            for file in files:
                ext = Path(file).suffix.lower()
                if ext == '.py':
                    languages.add('python')
                elif ext in ['.js', '.jsx']:
                    languages.add('javascript')
                elif ext in ['.ts', '.tsx']:
                    languages.add('typescript')

        return list(languages)

    async def _analyze_python(self, project_path: str) -> List[StaticIssue]:
        """分析Python代码 - 使用Pylint"""
        issues = []

        try:
            # 简化版: 只检查安全相关的问题
            # 实际应该运行 pylint,这里用正则匹配一些常见问题
            issues.extend(self._check_security_patterns(project_path, '.py'))

        except Exception as e:
            logger.error(f"Python分析失败: {e}")

        return issues

    async def _analyze_javascript(self, project_path: str) -> List[StaticIssue]:
        """分析JavaScript/TypeScript代码 - 使用ESLint"""
        issues = []

        try:
            # 简化版: 检查安全相关的问题
            issues.extend(self._check_security_patterns(project_path, '.js'))
            issues.extend(self._check_security_patterns(project_path, '.jsx'))
            issues.extend(self._check_security_patterns(project_path, '.ts'))
            issues.extend(self._check_security_patterns(project_path, '.tsx'))

        except Exception as e:
            logger.error(f"JavaScript分析失败: {e}")

        return issues

    def _check_security_patterns(self, project_path: str, extension: str) -> List[StaticIssue]:
        """
        检查常见的安全问题模式

        包括:
        - 硬编码密码/Token
        - SQL注入风险
        - XSS风险
        """
        issues = []

        # 安全模式定义
        patterns = [
            {
                'pattern': r'(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
                'severity': 'critical',
                'category': 'security',
                'rule': 'hardcoded-password',
                'message': '检测到硬编码密码,存在安全风险'
            },
            {
                'pattern': r'(api[_-]?key|secret[_-]?key|access[_-]?token)\s*=\s*["\'][^"\']+["\']',
                'severity': 'critical',
                'category': 'security',
                'rule': 'hardcoded-credentials',
                'message': '检测到硬编码的API密钥或Token'
            },
            {
                'pattern': r'(SELECT|INSERT|UPDATE|DELETE).*(WHERE|\+|concat).*\${?.*}?',
                'severity': 'critical',
                'category': 'security',
                'rule': 'sql-injection',
                'message': 'SQL注入风险: 直接拼接用户输入到SQL语句'
            },
            {
                'pattern': r'innerHTML\s*=\s*[^;]+',
                'severity': 'warning',
                'category': 'security',
                'rule': 'xss-risk',
                'message': 'XSS风险: 直接设置innerHTML可能导致跨站脚本攻击'
            },
            {
                'pattern': r'eval\s*\(',
                'severity': 'critical',
                'category': 'security',
                'rule': 'dangerous-eval',
                'message': '使用eval()函数存在代码注入风险'
            }
        ]

        # 遍历项目文件
        for root, _, files in os.walk(project_path):
            # 跳过排除目录
            if any(skip in root for skip in ['node_modules', 'venv', '.git', '__pycache__']):
                continue

            for file in files:
                if not file.endswith(extension):
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    # 检查每一行
                    for line_num, line_content in enumerate(lines, start=1):
                        for pattern_def in patterns:
                            if re.search(pattern_def['pattern'], line_content, re.IGNORECASE):
                                issues.append(StaticIssue(
                                    file_path=relative_path,
                                    line=line_num,
                                    severity=pattern_def['severity'],
                                    category=pattern_def['category'],
                                    rule=pattern_def['rule'],
                                    message=pattern_def['message']
                                ))

                except Exception as e:
                    logger.debug(f"读取文件失败 {file_path}: {e}")

        return issues

    def _severity_weight(self, severity: str) -> int:
        """计算严重程度权重"""
        weights = {
            'critical': 3,
            'warning': 2,
            'info': 1
        }
        return weights.get(severity.lower(), 0)
