import { useState } from 'react';
import BrutCard from './BrutCard';
import type { ReviewReport as ReviewReportType, ReviewIssue } from '../hooks/useTaskProgress';

interface ReviewReportProps {
  report: ReviewReportType;
}

const CATEGORY_NAMES: Record<string, string> = {
  security: '安全',
  performance: '性能',
  design: '设计',
  practice: '最佳实践'
};

const CATEGORY_COLORS: Record<string, string> = {
  security: '#EF4444',
  performance: '#F59E0B',
  design: '#3B82F6',
  practice: '#10B981'
};

/**
 * 代码审查报告组件
 * 遵循 Neo-Brutalism 设计风格
 */
export function ReviewReport({ report }: ReviewReportProps) {
  return (
    <div className="space-y-6">
      {/* 总体评分 */}
      <BrutCard variant="default">
        <div className="flex items-center gap-6">
          <ScoreGauge score={report.score} />
          <div className="flex-1">
            <h3 className="text-xl font-black mb-2">代码健康度</h3>
            <p className="text-sm text-gray-600 mb-4">{report.summary}</p>
            <div className="flex gap-4 text-sm">
              <span>审查文件: <strong>{report.reviewedFiles}/{report.totalFiles}</strong></span>
              <span>审查级别: <strong>{report.level}</strong></span>
            </div>
          </div>
        </div>
      </BrutCard>

      {/* 问题统计 */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="严重问题"
          count={report.criticalCount}
          bgColor="bg-red-100"
          borderColor="border-red-500"
        />
        <StatCard
          label="警告"
          count={report.warningCount}
          bgColor="bg-yellow-100"
          borderColor="border-yellow-500"
        />
        <StatCard
          label="提示"
          count={report.infoCount}
          bgColor="bg-blue-100"
          borderColor="border-blue-500"
        />
      </div>

      {/* 分类分布 */}
      <BrutCard variant="default">
        <h4 className="font-black mb-4">问题分类分布</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(report.issuesByCategory).map(([category, issues]) => (
            <div
              key={category}
              className="p-3 border-2 border-black"
              style={{ backgroundColor: `${CATEGORY_COLORS[category]}20` }}
            >
              <div className="text-2xl font-black">{issues.length}</div>
              <div className="text-sm">{CATEGORY_NAMES[category] || category}</div>
            </div>
          ))}
        </div>
      </BrutCard>

      {/* Top 问题列表 */}
      <BrutCard variant="default">
        <h4 className="font-black mb-4">Top {report.topIssues.length} 问题</h4>
        <div className="space-y-3">
          {report.topIssues.map((issue, idx) => (
            <IssueItem key={idx} issue={issue} />
          ))}
        </div>
      </BrutCard>
    </div>
  );
}

/**
 * 分数仪表盘
 */
function ScoreGauge({ score }: { score: number }) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return '#10B981';
    if (s >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const getScoreLabel = (s: number) => {
    if (s >= 80) return '优秀';
    if (s >= 60) return '良好';
    return '需改进';
  };

  const circumference = 2 * Math.PI * 45;
  const strokeDasharray = `${(score / 100) * circumference} ${circumference}`;

  return (
    <div className="relative w-32 h-32">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="64"
          cy="64"
          r="45"
          fill="none"
          stroke="#E5E7EB"
          strokeWidth="10"
        />
        <circle
          cx="64"
          cy="64"
          r="45"
          fill="none"
          stroke={getScoreColor(score)}
          strokeWidth="10"
          strokeDasharray={strokeDasharray}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-black">{score}</span>
        <span className="text-xs font-bold" style={{ color: getScoreColor(score) }}>
          {getScoreLabel(score)}
        </span>
      </div>
    </div>
  );
}

/**
 * 统计卡片
 */
function StatCard({
  label,
  count,
  bgColor,
  borderColor
}: {
  label: string;
  count: number;
  bgColor: string;
  borderColor: string;
}) {
  return (
    <div className={`p-4 border-2 border-black ${bgColor}`}>
      <div className={`text-3xl font-black border-l-4 pl-3 ${borderColor}`}>
        {count}
      </div>
      <div className="text-sm font-bold mt-1">{label}</div>
    </div>
  );
}

/**
 * 问题条目组件
 */
function IssueItem({ issue }: { issue: ReviewIssue }) {
  const [expanded, setExpanded] = useState(false);

  const severityConfig = {
    critical: { bg: 'bg-red-500', label: 'CRITICAL' },
    warning: { bg: 'bg-yellow-500', label: 'WARNING' },
    info: { bg: 'bg-blue-500', label: 'INFO' }
  };

  const config = severityConfig[issue.severity];

  return (
    <div className="border-2 border-black hover:shadow-brut-sm transition-shadow">
      {/* 头部 */}
      <div
        className="p-4 cursor-pointer flex items-start justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 text-xs font-bold text-white ${config.bg}`}>
              {config.label}
            </span>
            <span className="text-xs font-bold text-gray-500">
              {CATEGORY_NAMES[issue.category]}
            </span>
            <span className="text-xs text-gray-400">
              via {issue.source === 'llm' ? 'LLM' : '静态分析'}
            </span>
          </div>
          <div className="font-bold">{issue.message}</div>
          <div className="text-sm text-gray-600 mt-1 font-mono">
            {issue.filePath}:{issue.line}
          </div>
        </div>
        <button className="text-xl font-bold px-2">
          {expanded ? '-' : '+'}
        </button>
      </div>

      {/* 展开内容 */}
      {expanded && (
        <div className="p-4 border-t-2 border-black bg-gray-50 space-y-4">
          {issue.reason && (
            <div>
              <div className="font-bold text-sm mb-1">问题原因</div>
              <p className="text-sm">{issue.reason}</p>
            </div>
          )}
          {issue.suggestion && (
            <div>
              <div className="font-bold text-sm mb-1">改进建议</div>
              <p className="text-sm bg-green-50 p-3 border-l-4 border-green-500">
                {issue.suggestion}
              </p>
            </div>
          )}
          {issue.example && (
            <div>
              <div className="font-bold text-sm mb-1">修复示例</div>
              <pre className="text-sm bg-white p-3 border-2 border-green-500 overflow-x-auto">
                {issue.example}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
