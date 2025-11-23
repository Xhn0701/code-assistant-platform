import { useState, useEffect, useCallback, useRef } from 'react';
import { Client, type IMessage } from '@stomp/stompjs';
import SockJS from 'sockjs-client';
import { WS_BASE_URL } from '../services/api';

export interface TaskProgress {
  taskId: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  progress: number;
  message: string;
  result?: ReviewReport;
  error?: string;
}

export interface ReviewReport {
  projectId: number;
  score: number;
  level: string;
  totalFiles: number;
  reviewedFiles: number;
  totalIssues: number;
  criticalCount: number;
  warningCount: number;
  infoCount: number;
  issuesByCategory: Record<string, ReviewIssue[]>;
  topIssues: ReviewIssue[];
  summary: string;
  createdAt: string;
}

export interface ReviewIssue {
  filePath: string;
  line: number;
  severity: 'critical' | 'warning' | 'info';
  category: 'security' | 'performance' | 'design' | 'practice';
  message: string;
  reason?: string;
  suggestion?: string;
  example?: string;
  source: 'static' | 'llm';
}

interface UseTaskProgressOptions {
  onComplete?: (report: ReviewReport) => void;
  onError?: (error: string) => void;
}

// 将后端返回的审查报告（snake_case）转换为前端使用的 camelCase 结构
function mapReviewIssue(raw: any): ReviewIssue {
  return {
    filePath: raw.file_path,
    line: raw.line,
    severity: raw.severity,
    category: raw.category,
    message: raw.message,
    reason: raw.reason || undefined,
    suggestion: raw.suggestion || undefined,
    example: raw.example || undefined,
    source: raw.source === 'static' ? 'static' : 'llm'
  };
}

function mapReviewReport(raw: any): ReviewReport {
  if (!raw) {
    // 兜底，避免空对象导致前端崩溃
    return {
      projectId: 0,
      score: 0,
      level: '',
      totalFiles: 0,
      reviewedFiles: 0,
      totalIssues: 0,
      criticalCount: 0,
      warningCount: 0,
      infoCount: 0,
      issuesByCategory: {},
      topIssues: [],
      summary: '',
      createdAt: ''
    };
  }

  const issuesByCategory: Record<string, ReviewIssue[]> = {};
  if (raw.issues_by_category && typeof raw.issues_by_category === 'object') {
    Object.entries(raw.issues_by_category).forEach(([category, issues]) => {
      issuesByCategory[category] = Array.isArray(issues)
        ? (issues as any[]).map(mapReviewIssue)
        : [];
    });
  }

  const topIssues: ReviewIssue[] = Array.isArray(raw.top_issues)
    ? (raw.top_issues as any[]).map(mapReviewIssue)
    : [];

  return {
    projectId: raw.project_id ?? 0,
    score: raw.score ?? 0,
    level: raw.level ?? '',
    totalFiles: raw.total_files ?? 0,
    reviewedFiles: raw.reviewed_files ?? 0,
    totalIssues: raw.total_issues ?? 0,
    criticalCount: raw.critical_count ?? 0,
    warningCount: raw.warning_count ?? 0,
    infoCount: raw.info_count ?? 0,
    issuesByCategory,
    topIssues,
    summary: raw.summary ?? '',
    createdAt: raw.created_at ?? ''
  };
}

// 将后端 TaskProgress JSON 转换为前端的 TaskProgress 类型
function mapTaskProgress(raw: any): TaskProgress {
  // 统一任务状态到前端定义的枚举
  let status: TaskProgress['status'];
  switch (raw.status) {
    case 'COMPLETED':
    case 'SUCCESS':
      status = 'COMPLETED';
      break;
    case 'FAILED':
    case 'FAILURE':
      status = 'FAILED';
      break;
    case 'RUNNING':
    case 'PROGRESS':
      status = 'RUNNING';
      break;
    case 'PENDING':
    default:
      status = 'PENDING';
      break;
  }

  const mapped: TaskProgress = {
    taskId: String(raw.taskId ?? ''),
    status,
    progress: typeof raw.progress === 'number' ? raw.progress : 0,
    message: raw.message ?? '',
    result: undefined,
    error: raw.error
  };

  if (raw.result) {
    mapped.result = mapReviewReport(raw.result);
  }

  return mapped;
}

/**
 * WebSocket Hook - 订阅任务进度
 * 使用 STOMP 协议 + SockJS 降级方案
 */
export function useTaskProgress(
  taskId: string | null,
  options?: UseTaskProgressOptions
) {
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [connected, setConnected] = useState(false);
  const clientRef = useRef<Client | null>(null);
  const optionsRef = useRef<UseTaskProgressOptions | undefined>(options);

  // 始终使用最新的回调，避免因为 options 变化频繁重连
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);

  // 连接 WebSocket
  const connect = useCallback(() => {
    if (!taskId || clientRef.current?.connected) return;

    const client = new Client({
      webSocketFactory: () => new SockJS(WS_BASE_URL),
      reconnectDelay: 5000,
      heartbeatIncoming: 4000,
      heartbeatOutgoing: 4000,
      debug: (str) => {
        if (import.meta.env.DEV) {
          console.log('[STOMP]', str);
        }
      },
      onConnect: () => {
        setConnected(true);
        console.log('[WebSocket] Connected');

        // 订阅任务进度
        client.subscribe(`/topic/task/${taskId}`, (message: IMessage) => {
          try {
            const raw = JSON.parse(message.body);
            const data: TaskProgress = mapTaskProgress(raw);
            setProgress(data);

            // 任务完成回调
            if (data.status === 'COMPLETED' && data.result) {
              optionsRef.current?.onComplete?.(data.result);
            }

            // 任务失败回调
            if (data.status === 'FAILED') {
              const errMsg = data.error || data.message || '任务失败';
              optionsRef.current?.onError?.(errMsg);
            }
          } catch (err) {
            console.error('[WebSocket] Parse error:', err);
          }
        });
      },
      onDisconnect: () => {
        setConnected(false);
        console.log('[WebSocket] Disconnected');
      },
      onStompError: (frame) => {
        console.error('[WebSocket] STOMP error:', frame.headers['message']);
      }
    });

    client.activate();
    clientRef.current = client;
  }, [taskId]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (clientRef.current?.connected) {
      clientRef.current.deactivate();
      clientRef.current = null;
    }
    setConnected(false);
    setProgress(null);
  }, []);

  // 当 taskId 变化时自动连接/断开
  useEffect(() => {
    if (taskId) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [taskId, connect, disconnect]);

  return {
    progress,
    connected,
    disconnect
  };
}
