"""
智能代码审查 Agent
结合静态分析和 LLM 深度审查,提供多维度代码质量报告
"""
import asyncio
import json
import logging
import os
import re
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from app.models.review import (
    StaticIssue,
    Issue,
    ReviewReport,
    CodeFile
)
from app.analyzers.static_analyzer import StaticAnalyzer

logger = logging.getLogger(__name__)

# LLM Prompt 设计 (优化后的版本)
REVIEW_SYSTEM_PROMPT = """
你是一位拥有10年经验的资深代码审查专家。

⚠️ 重要原则:
1. **避免误报**: 宁可漏报,不要误报。只报告有明确证据的问题。
2. **考虑上下文**: 理解框架特性 (React Hooks、Vue响应式等)
3. **区分测试代码**: 测试代码可以有硬编码、简化逻辑
4. **聚焦高价值问题**: 优先报告安全和性能问题,而非代码风格

审查维度 (优先级排序):
1. 🔒 **安全漏洞** (P0 - 必须报告)
   - SQL注入、XSS、敏感数据泄露、不安全的依赖

2. ⚡ **性能问题** (P1 - 重要)
   - N+1查询、内存泄漏、低效算法、不必要的重渲染

3. 📐 **设计问题** (P2 - 酌情报告)
   - 严重违反SOLID原则、过度耦合、明显的代码重复

4. ✅ **最佳实践** (P3 - 仅报告严重情况)
   - 缺少关键错误处理、关键业务逻辑无日志

❌ **不要报告**:
- 代码风格问题 (缩进、命名) - 应由Linter处理
- 个人偏好
- 框架正常用法

输出格式 (严格JSON):
{
  "issues": [
    {
      "severity": "critical|warning|info",
      "category": "security|performance|design|practice",
      "line": 行号,
      "message": "问题描述 (简洁、技术准确)",
      "evidence": "问题证据 (引用具体代码)",
      "impact": "潜在影响 (用户视角)",
      "suggestion": "改进建议 (可操作)",
      "example": "修复示例代码 (可选)"
    }
  ]
}
"""

REVIEW_USER_PROMPT_TEMPLATE = """
请审查以下{language}代码文件:

文件路径: {file_path}
代码行数: {line_count}

代码内容:
```{language}
{code_content}
```

{static_issues_context}

请重点关注:
1. 静态分析未覆盖的深层问题
2. 架构设计和代码可维护性
3. 潜在的性能瓶颈和安全风险

请输出JSON格式的审查结果。
"""


class ReviewAgent:
    """智能代码审查Agent"""

    def __init__(self, openai_api_key: Optional[str] = None):
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("需要配置 OPENAI_API_KEY 环境变量")

        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,  # 确定性输出
            max_tokens=2000,
            api_key=api_key
        )
        self.static_analyzer = StaticAnalyzer()

    async def review_code(
        self,
        project_id: int,
        project_path: str,
        files: Optional[List[str]] = None,
        level: str = "standard"
    ) -> ReviewReport:
        """
        执行代码审查

        Args:
            project_id: 项目ID
            project_path: 项目根目录路径
            files: 指定文件列表 (None=全部)
            level: 审查深度
                - quick: 仅静态分析
                - standard: 静态分析 + LLM审查核心文件
                - full: 静态分析 + LLM审查所有文件
        """
        logger.info(f"开始代码审查: project_id={project_id}, level={level}")

        # 1. 加载项目代码
        code_files = await self._load_code_files(project_path, files)
        logger.info(f"加载了 {len(code_files)} 个代码文件")

        # 2. 静态分析 (全量)
        static_issues = await self.static_analyzer.analyze_project(project_path)
        logger.info(f"静态分析发现 {len(static_issues)} 个问题")

        # 3. LLM 深度审查 (按level决定范围)
        llm_issues = []
        if level in ['standard', 'full']:
            selected_files = self._select_files_for_llm(
                code_files,
                static_issues,
                level
            )
            logger.info(f"选择 {len(selected_files)} 个文件进行LLM审查")

            llm_issues = await self._llm_review_batch(
                selected_files,
                static_issues
            )
            logger.info(f"LLM审查发现 {len(llm_issues)} 个问题")

        # 4. 合并结果并生成报告
        report = self._generate_report(
            project_id=project_id,
            static_issues=static_issues,
            llm_issues=llm_issues,
            level=level,
            total_files=len(code_files)
        )

        logger.info(f"代码审查完成: score={report.score}, issues={report.total_issues}")
        return report

    async def _load_code_files(
        self,
        project_path: str,
        files: Optional[List[str]]
    ) -> List[CodeFile]:
        """加载代码文件"""
        code_files = []

        # 支持的代码文件扩展名
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java'}

        if files:
            # 加载指定文件
            for file_path in files:
                full_path = os.path.join(project_path, file_path)
                if os.path.exists(full_path):
                    code_files.append(self._read_code_file(full_path, project_path))
        else:
            # 加载所有代码文件
            for root, _, filenames in os.walk(project_path):
                # 跳过排除目录
                if any(skip in root for skip in ['node_modules', 'venv', '.git', '__pycache__', 'dist', 'build']):
                    continue

                for filename in filenames:
                    if Path(filename).suffix in code_extensions:
                        full_path = os.path.join(root, filename)
                        code_files.append(self._read_code_file(full_path, project_path))

        return code_files

    def _read_code_file(self, full_path: str, project_path: str) -> CodeFile:
        """读取单个代码文件"""
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            relative_path = os.path.relpath(full_path, project_path)
            language = self._detect_language(full_path)

            return CodeFile(
                path=relative_path,
                language=language,
                content=content
            )
        except Exception as e:
            logger.error(f"读取文件失败 {full_path}: {e}")
            return CodeFile(path="error", language="unknown", content="")

    def _detect_language(self, file_path: str) -> str:
        """根据文件扩展名检测语言"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java'
        }
        return lang_map.get(ext, 'unknown')

    def _select_files_for_llm(
        self,
        code_files: List[CodeFile],
        static_issues: List[StaticIssue],
        level: str
    ) -> List[CodeFile]:
        """智能选择需要LLM审查的文件"""
        if level == 'full':
            return code_files

        # standard模式: 只审查有问题的文件 + 核心文件
        selected = set()

        # 1. 有严重问题的文件
        for issue in static_issues:
            if issue.severity in ['critical', 'warning']:
                selected.add(issue.file_path)

        # 2. 核心文件 (根据路径判断)
        for file in code_files:
            if self._is_core_file(file.path):
                selected.add(file.path)

        # 3. 限制数量 (防止成本过高)
        MAX_FILES = 20
        selected_files = [f for f in code_files if f.path in selected]

        return selected_files[:MAX_FILES]

    def _is_core_file(self, file_path: str) -> bool:
        """判断是否为核心文件"""
        core_patterns = [
            r'/controller/',
            r'/service/',
            r'/api/',
            r'/models?/',
            r'/auth',
            r'/security'
        ]
        return any(re.search(pattern, file_path.lower()) for pattern in core_patterns)

    async def _llm_review_batch(
        self,
        files: List[CodeFile],
        static_issues: List[StaticIssue]
    ) -> List[Issue]:
        """批量LLM审查 (带并发控制)"""
        issues = []

        # 并发控制: 同时最多5个LLM调用
        semaphore = asyncio.Semaphore(5)

        async def review_single_file(file: CodeFile):
            async with semaphore:
                return await self._llm_review_file(file, static_issues)

        # 并发执行
        tasks = [review_single_file(f) for f in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 收集结果 (忽略异常)
        for result in results:
            if isinstance(result, list):
                issues.extend(result)
            else:
                logger.error(f"LLM review failed: {result}")

        return issues

    async def _llm_review_file(
        self,
        file: CodeFile,
        static_issues: List[StaticIssue]
    ) -> List[Issue]:
        """LLM审查单个文件"""
        # 构建上下文: 该文件的静态分析结果
        file_static_issues = [
            i for i in static_issues if i.file_path == file.path
        ]

        static_context = ""
        if file_static_issues:
            static_context = "静态分析已发现以下问题:\n"
            for issue in file_static_issues:
                static_context += f"- [{issue.severity}] {issue.message} (行{issue.line})\n"
            static_context += "\n请关注静态分析未覆盖的深层问题。"

        # 调用LLM
        messages = [
            SystemMessage(content=REVIEW_SYSTEM_PROMPT),
            HumanMessage(content=REVIEW_USER_PROMPT_TEMPLATE.format(
                language=file.language,
                file_path=file.path,
                line_count=file.line_count,
                code_content=file.content[:5000],  # 限制长度
                static_issues_context=static_context
            ))
        ]

        try:
            response = await self.llm.ainvoke(messages)
            result = json.loads(response.content)

            # 转换为统一的Issue格式
            issues = []
            for item in result.get('issues', []):
                issues.append(Issue(
                    file_path=file.path,
                    line=item.get('line', 0),
                    severity=item['severity'],
                    category=item['category'],
                    message=item['message'],
                    evidence=item.get('evidence', ''),
                    impact=item.get('impact', ''),
                    suggestion=item.get('suggestion', ''),
                    example=item.get('example', ''),
                    source='llm'
                ))

            return issues

        except Exception as e:
            logger.error(f"LLM review error for {file.path}: {e}")
            return []

    def _generate_report(
        self,
        project_id: int,
        static_issues: List[StaticIssue],
        llm_issues: List[Issue],
        level: str,
        total_files: int
    ) -> ReviewReport:
        """生成审查报告"""
        # 合并所有问题
        all_issues = self._merge_issues(static_issues, llm_issues)

        # 按严重程度分组
        critical = [i for i in all_issues if i.severity == 'critical']
        warnings = [i for i in all_issues if i.severity == 'warning']
        infos = [i for i in all_issues if i.severity == 'info']

        # 计算评分
        score = 100
        score -= len(critical) * 10
        score -= len(warnings) * 3
        score -= len(infos) * 1
        score = max(0, score)

        # 按类别分组
        by_category = self._group_by_category(all_issues)

        # 生成总结
        summary = self._generate_summary(critical, warnings, infos, by_category)

        return ReviewReport(
            project_id=project_id,
            score=score,
            level=level,
            total_files=total_files,
            reviewed_files=len(set(i.file_path for i in all_issues)),
            total_issues=len(all_issues),
            critical_count=len(critical),
            warning_count=len(warnings),
            info_count=len(infos),
            issues_by_category=by_category,
            top_issues=self._get_top_issues(all_issues, limit=10),
            summary=summary,
            created_at=datetime.now()
        )

    def _merge_issues(
        self,
        static_issues: List[StaticIssue],
        llm_issues: List[Issue]
    ) -> List[Issue]:
        """合并静态分析和LLM的问题"""
        all_issues = []

        # 转换静态问题为统一格式
        for si in static_issues:
            all_issues.append(Issue(
                file_path=si.file_path,
                line=si.line,
                severity=si.severity,
                category=si.category,
                message=si.message,
                reason=f"静态分析规则: {si.rule}",
                source='static'
            ))

        # 添加LLM问题
        all_issues.extend(llm_issues)

        return all_issues

    def _group_by_category(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """按类别分组"""
        by_category = {}
        for issue in issues:
            cat = issue.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(issue)
        return by_category

    def _get_top_issues(self, issues: List[Issue], limit: int) -> List[Issue]:
        """获取Top问题"""
        # 按严重程度排序
        sorted_issues = sorted(
            issues,
            key=lambda x: (
                {'critical': 3, 'warning': 2, 'info': 1}.get(x.severity, 0),
                x.line
            ),
            reverse=True
        )
        return sorted_issues[:limit]

    def _generate_summary(
        self,
        critical: List[Issue],
        warnings: List[Issue],
        infos: List[Issue],
        by_category: Dict[str, List[Issue]]
    ) -> str:
        """生成人类可读的总结"""
        summary_parts = []

        if critical:
            summary_parts.append(f"⚠️ 发现 {len(critical)} 个严重问题,需要立即修复")

        if warnings:
            summary_parts.append(f"🔸 发现 {len(warnings)} 个警告,建议尽快处理")

        # 类别总结
        if by_category:
            sorted_categories = sorted(
                by_category.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )
            if sorted_categories:
                top_cat, top_issues = sorted_categories[0]
                cat_name = {
                    'security': '安全',
                    'performance': '性能',
                    'design': '设计',
                    'practice': '最佳实践'
                }.get(top_cat, top_cat)
                summary_parts.append(f"📊 主要问题集中在{cat_name}方面 ({len(top_issues)}个)")

        return "；".join(summary_parts) + "。" if summary_parts else "代码质量良好,未发现明显问题。"
