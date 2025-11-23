# Phase 6 开发计划：服务端到端集成和高级特性

> **版本**: v1.0
> **创建时间**: 2025-11-21
> **预计周期**: 3-4周
> **目标**: 完成Java-Python服务集成、代码审查Agent、异步任务处理

---

## 📋 目录

- [总体目标](#总体目标)
- [架构设计](#架构设计)
- [功能模块](#功能模块)
- [技术选型](#技术选型)
- [实现方案](#实现方案)
- [任务分解](#任务分解)
- [时间规划](#时间规划)
- [测试策略](#测试策略)
- [已知风险](#已知风险)

---

## 总体目标

### 核心目标

**完成度目标**: Phase 6 达到 100% 完成

**核心交付物**:
1. ✅ Java ↔ Python 服务端到端集成
2. ✅ 代码审查 Agent (静态分析 + LLM)
3. ✅ 异步任务处理系统 (索引、审查)
4. ✅ WebSocket 实时推送
5. ✅ 性能优化和监控

### 业务价值

- **用户体验**: 从项目创建到代码问答的完整闭环
- **智能审查**: 自动化代码质量检查
- **实时反馈**: 长时间任务的进度实时推送
- **系统稳定**: 异步处理提升并发能力

---

## 架构设计

### 1. 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (React)                             │
│  - 项目创建 → 自动触发索引                                        │
│  - WebSocket连接 → 实时接收进度                                  │
│  - 代码审查按钮 → 查看审查报告                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                    Java 业务服务 (Spring Boot)                   │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ ProjectService   │────────→│ AgentClientService│             │
│  │ - 创建项目       │         │ - HTTP调用Python │             │
│  │ - 触发索引       │         │ - 统一错误处理   │             │
│  └──────────────────┘         └──────────────────┘             │
│           ↓                            ↓                         │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ TaskService      │←────────│ WebSocketHandler │             │
│  │ - 任务队列管理   │         │ - 进度推送       │             │
│  │ - 状态轮询       │         └──────────────────┘             │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP REST API
┌─────────────────────────────────────────────────────────────────┐
│                   Python Agent 服务 (FastAPI)                    │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ IndexService     │         │ ReviewAgent      │             │
│  │ - 代码索引       │         │ - 静态分析       │             │
│  │ - 状态回调       │         │ - LLM深度审查    │             │
│  └──────────────────┘         └──────────────────┘             │
│           ↓                            ↓                         │
│  ┌──────────────────────────────────────────────┐               │
│  │         Celery 异步任务队列                  │               │
│  │  - 索引任务 (index_repository_task)         │               │
│  │  - 审查任务 (review_code_task)               │               │
│  │  - 任务状态管理 (TaskResult)                 │               │
│  └──────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       数据存储层                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │PostgreSQL│  │  Redis   │  │ ChromaDB │  │  Celery  │       │
│  │- 任务记录│  │- 任务队列│  │- 向量库  │  │- Result  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### 2. 服务间通信流程

#### 场景1: 用户创建项目并索引代码

```
用户 → 前端 → Java ProjectService
                    ↓
        1. 创建项目记录 (PostgreSQL)
                    ↓
        2. 调用 AgentClientService.indexRepository()
                    ↓ HTTP POST /api/v1/index/repository
              Python IndexService
                    ↓
        3. 提交到 Celery 异步队列
                    ↓
              Celery Worker 执行索引
                    ↓
        4. 定期更新状态到 Redis
                    ↓
        5. Java 轮询状态 (或接收回调)
                    ↓
        6. WebSocket 推送进度到前端
                    ↓
              前端实时显示进度条
```

#### 场景2: 用户请求代码审查

```
用户 → 前端 → Java ProjectService
                    ↓
        1. 创建审查任务 (PostgreSQL)
                    ↓
        2. 调用 AgentClientService.reviewCode()
                    ↓ HTTP POST /api/v1/review/analyze
              Python ReviewAgent
                    ↓
        3. 提交到 Celery 异步队列
                    ↓
              Celery Worker 执行审查
                    ├─→ 静态分析 (ESLint/Pylint)
                    └─→ LLM 深度审查
                    ↓
        4. 生成审查报告 (JSON)
                    ↓
        5. 保存报告到 PostgreSQL
                    ↓
        6. WebSocket 推送完成通知
                    ↓
              前端展示审查结果
```

---

## 功能模块

### 模块1: Java-Python 服务集成层

#### 1.1 AgentClientService (Java)

**职责**: 封装对Python服务的HTTP调用

**核心功能**:
- 索引仓库 (`indexRepository()`)
- 查询索引状态 (`getIndexStatus()`)
- 代码问答 (`askQuestion()`)
- 代码审查 (`reviewCode()`)
- 统一异常处理和重试机制

**技术实现**:
```java
@Service
@RequiredArgsConstructor
@Slf4j
public class AgentClientService {

    private final RestTemplate restTemplate;
    private final AgentServiceConfig config;

    /**
     * 索引仓库代码
     */
    public IndexResponse indexRepository(Long projectId, String repoPath) {
        String url = config.getBaseUrl() + "/api/v1/index/repository";

        IndexRequest request = IndexRequest.builder()
            .projectId(projectId)
            .repositoryUrl(repoPath)
            .build();

        try {
            ResponseEntity<AgentResult<IndexResponse>> response =
                restTemplate.postForEntity(url, request,
                    new ParameterizedTypeReference<>() {});

            return response.getBody().getData();
        } catch (RestClientException e) {
            log.error("Failed to call index API: {}", e.getMessage());
            throw new AgentServiceException("索引服务调用失败", e);
        }
    }

    /**
     * 代码审查
     */
    public ReviewResponse reviewCode(Long projectId, ReviewLevel level) {
        // 类似实现
    }
}
```

**配置类**:
```java
@Configuration
@ConfigurationProperties(prefix = "agent-service")
@Data
public class AgentServiceConfig {
    private String baseUrl = "http://localhost:8000";
    private int connectTimeout = 5000;
    private int readTimeout = 30000;
    private int maxRetries = 3;
}
```

#### 1.2 统一错误处理

**异常体系**:
```java
// 自定义异常
public class AgentServiceException extends RuntimeException {
    private final AgentErrorCode errorCode;
    private final String detail;
}

// 错误码枚举
public enum AgentErrorCode {
    SERVICE_UNAVAILABLE(5001, "Agent服务不可用"),
    INDEX_FAILED(5002, "代码索引失败"),
    REVIEW_FAILED(5003, "代码审查失败"),
    TIMEOUT(5004, "请求超时");
}

// 全局异常处理
@ControllerAdvice
public class AgentExceptionHandler {

    @ExceptionHandler(AgentServiceException.class)
    public Result<?> handleAgentException(AgentServiceException e) {
        log.error("Agent service error: {}", e.getMessage());
        return Result.error(e.getErrorCode().getCode(),
                           e.getMessage(),
                           e.getDetail());
    }
}
```

---

### 模块2: 代码审查 Agent

#### 2.1 架构设计

**两阶段审查策略**:

```
阶段1: 静态分析 (Fast & Deterministic)
    ├─→ ESLint (JavaScript/TypeScript)
    ├─→ Pylint/Flake8 (Python)
    ├─→ Checkstyle (Java)
    └─→ 输出: 语法错误、编码规范问题

阶段2: LLM 深度审查 (Slow & Intelligent)
    ├─→ 提取问题代码片段
    ├─→ LLM 分析 (安全、性能、设计)
    └─→ 输出: 改进建议、最佳实践
```

#### 2.2 ReviewAgent 实现

**Python 实现**:
```python
# app/agents/review_agent.py

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class ReviewAgent:
    """代码审查 Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.static_analyzers = {
            'python': PylintAnalyzer(),
            'javascript': ESLintAnalyzer(),
            'java': CheckstyleAnalyzer()
        }

    async def review_code(
        self,
        project_id: int,
        files: List[str] = None,
        level: str = "standard"
    ) -> ReviewReport:
        """
        执行代码审查

        Args:
            project_id: 项目ID
            files: 指定文件列表(None=全部)
            level: quick/standard/full

        Returns:
            ReviewReport: 审查报告
        """
        # 1. 加载代码文件
        code_files = await self._load_code_files(project_id, files)

        # 2. 静态分析
        static_issues = await self._static_analysis(code_files)

        # 3. LLM 深度审查 (根据level决定)
        llm_issues = []
        if level in ['standard', 'full']:
            llm_issues = await self._llm_review(code_files, static_issues)

        # 4. 生成报告
        report = self._generate_report(
            static_issues,
            llm_issues,
            level
        )

        return report

    async def _llm_review(
        self,
        code_files: List[CodeFile],
        static_issues: List[Issue]
    ) -> List[Issue]:
        """LLM 深度审查"""

        prompt = PromptTemplate.from_template("""
你是一位资深代码审查专家。请审查以下代码，关注：

1. **安全问题**: SQL注入、XSS、密码硬编码等
2. **性能问题**: N+1查询、内存泄漏、低效算法
3. **设计问题**: 违反SOLID原则、过度耦合、代码重复
4. **最佳实践**: 命名规范、注释质量、错误处理

代码文件: {file_path}
```{language}
{code_content}
```

已知静态分析问题:
{static_issues}

请输出JSON格式的审查结果:
{{
  "issues": [
    {{
      "severity": "critical|warning|info",
      "category": "security|performance|design|practice",
      "line": 行号,
      "message": "问题描述",
      "suggestion": "改进建议",
      "example": "示例代码(可选)"
    }}
  ]
}}
""")

        issues = []
        for file in code_files:
            # 限制：只审查有静态问题的文件或核心文件
            if not self._should_llm_review(file, static_issues):
                continue

            result = await self.llm.ainvoke(
                prompt.format(
                    file_path=file.path,
                    language=file.language,
                    code_content=file.content,
                    static_issues=self._format_static_issues(file, static_issues)
                )
            )

            file_issues = self._parse_llm_result(result.content)
            issues.extend(file_issues)

        return issues

    def _generate_report(
        self,
        static_issues: List[Issue],
        llm_issues: List[Issue],
        level: str
    ) -> ReviewReport:
        """生成审查报告"""

        all_issues = static_issues + llm_issues

        # 计算总体评分 (0-100)
        score = self._calculate_score(all_issues)

        # 按严重程度分类
        critical = [i for i in all_issues if i.severity == 'critical']
        warnings = [i for i in all_issues if i.severity == 'warning']
        infos = [i for i in all_issues if i.severity == 'info']

        return ReviewReport(
            score=score,
            level=level,
            total_issues=len(all_issues),
            critical_count=len(critical),
            warning_count=len(warnings),
            info_count=len(infos),
            issues=all_issues,
            summary=self._generate_summary(all_issues)
        )
```

**API 接口**:
```python
# app/api/v1/review.py

@router.post("/analyze", response_model=ResponseModel[ReviewTaskResponse])
async def analyze_code(
    request: ReviewRequest,
    review_agent: ReviewAgent = Depends(get_review_agent)
):
    """
    提交代码审查任务

    Request:
        - projectId: 项目ID
        - files: 指定文件列表 (可选)
        - level: quick/standard/full

    Response:
        - taskId: 任务ID
        - status: PENDING
        - estimatedTime: 预估时间(秒)
    """
    # 创建异步任务
    task = review_code_task.delay(
        project_id=request.projectId,
        files=request.files,
        level=request.level
    )

    return ResponseModel.success(
        ReviewTaskResponse(
            taskId=task.id,
            status="PENDING",
            estimatedTime=estimate_review_time(request)
        )
    )

@router.get("/result/{task_id}", response_model=ResponseModel[ReviewReport])
async def get_review_result(task_id: str):
    """查询审查结果"""
    result = AsyncResult(task_id)

    if not result.ready():
        return ResponseModel.error(
            code=3001,
            message="审查任务进行中",
            data={"progress": result.info.get('progress', 0)}
        )

    if result.failed():
        return ResponseModel.error(
            code=3002,
            message="审查任务失败",
            data={"error": str(result.info)}
        )

    report = result.result
    return ResponseModel.success(report)
```

---

### 模块3: 异步任务处理系统

#### 3.1 Celery 配置

**Python 配置**:
```python
# app/core/celery_app.py

from celery import Celery
from app.config import settings

celery_app = Celery(
    "code_assistant",
    broker=settings.celery_broker_url,  # redis://localhost:6379/0
    backend=settings.celery_result_backend  # redis://localhost:6379/1
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
    task_soft_time_limit=3300,  # 55分钟软超时
    worker_prefetch_multiplier=1,  # 一次只取一个任务
    worker_max_tasks_per_child=100,  # 避免内存泄漏
)
```

#### 3.2 索引任务实现

```python
# app/tasks/index_tasks.py

from app.core.celery_app import celery_app
from app.services.code_indexer import CodeIndexer
from celery import Task

class CallbackTask(Task):
    """支持进度回调的任务基类"""

    def update_progress(self, current, total, message=""):
        """更新任务进度"""
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current,
                'total': total,
                'percent': int(current / total * 100),
                'message': message
            }
        )

@celery_app.task(bind=True, base=CallbackTask)
def index_repository_task(
    self,
    project_id: int,
    repository_url: str
) -> dict:
    """
    异步索引代码仓库

    支持进度更新和状态回调
    """
    try:
        # 0. 初始化
        self.update_progress(0, 100, "正在初始化索引器...")
        indexer = CodeIndexer()

        # 1. 加载代码文件
        self.update_progress(10, 100, "正在扫描代码文件...")
        code_files = indexer.load_repository(repository_url)
        total_files = len(code_files)

        # 2. 分块处理
        self.update_progress(30, 100, f"正在分块处理 {total_files} 个文件...")
        chunks = indexer.split_files(code_files)

        # 3. 向量化 + 存储 (带进度)
        indexed_count = 0
        for i, batch in enumerate(chunk_batch(chunks, batch_size=10)):
            self.update_progress(
                30 + int(i / len(chunks) * 60),
                100,
                f"正在索引 {indexed_count}/{total_files} 个文件..."
            )

            indexer.index_batch(batch, project_id)
            indexed_count += len(batch)

        # 4. 完成
        self.update_progress(100, 100, "索引完成")

        return {
            "projectId": project_id,
            "totalFiles": total_files,
            "indexedFiles": indexed_count,
            "status": "COMPLETED"
        }

    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
```

#### 3.3 任务状态管理 (Java)

```java
// Java 端任务管理
@Service
public class TaskService {

    @Autowired
    private TaskRepository taskRepository;

    @Autowired
    private SimpMessagingTemplate messagingTemplate;

    /**
     * 轮询任务状态并推送到前端
     */
    @Scheduled(fixedDelay = 2000)  // 每2秒轮询一次
    public void pollTaskStatus() {
        List<Task> runningTasks = taskRepository
            .findByStatus(TaskStatus.RUNNING);

        for (Task task : runningTasks) {
            // 查询 Python 服务状态
            TaskStatusResponse status = agentClient
                .getTaskStatus(task.getTaskId());

            // 更新本地状态
            task.setProgress(status.getProgress());
            task.setMessage(status.getMessage());

            if (status.isCompleted()) {
                task.setStatus(TaskStatus.COMPLETED);
                task.setResult(status.getResult());
            }

            taskRepository.save(task);

            // WebSocket 推送到前端
            messagingTemplate.convertAndSend(
                "/topic/task/" + task.getId(),
                status
            );
        }
    }
}
```

---

### 模块4: WebSocket 实时通信

#### 4.1 Java WebSocket 配置

```java
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        // 配置消息代理
        config.enableSimpleBroker("/topic", "/queue");
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
            .setAllowedOrigins("http://localhost:5173")
            .withSockJS();
    }
}

@Controller
public class TaskWebSocketController {

    @Autowired
    private SimpMessagingTemplate messagingTemplate;

    /**
     * 推送任务进度
     */
    public void sendTaskProgress(Long taskId, TaskProgress progress) {
        messagingTemplate.convertAndSend(
            "/topic/task/" + taskId,
            progress
        );
    }

    /**
     * 推送任务完成通知
     */
    public void sendTaskComplete(Long taskId, Object result) {
        messagingTemplate.convertAndSend(
            "/topic/task/" + taskId,
            TaskCompleteEvent.builder()
                .taskId(taskId)
                .status("COMPLETED")
                .result(result)
                .timestamp(System.currentTimeMillis())
                .build()
        );
    }
}
```

#### 4.2 前端 WebSocket 集成

```typescript
// web-client/src/hooks/useTaskProgress.ts

import { useEffect, useState } from 'react';
import SockJS from 'sockjs-client';
import { Client } from '@stomp/stompjs';

interface TaskProgress {
  current: number;
  total: number;
  percent: number;
  message: string;
}

export function useTaskProgress(taskId: number | null) {
  const [progress, setProgress] = useState<TaskProgress | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const socket = new SockJS('http://localhost:8080/ws');
    const client = new Client({
      webSocketFactory: () => socket,
      onConnect: () => {
        // 订阅任务进度
        client.subscribe(`/topic/task/${taskId}`, (message) => {
          const data = JSON.parse(message.body);

          if (data.status === 'COMPLETED') {
            setIsComplete(true);
            setProgress({ ...data, percent: 100 });
          } else if (data.status === 'FAILED') {
            setError(data.error);
          } else {
            setProgress(data);
          }
        });
      },
      onStompError: (frame) => {
        setError('WebSocket连接失败');
      }
    });

    client.activate();

    return () => {
      client.deactivate();
    };
  }, [taskId]);

  return { progress, isComplete, error };
}
```

**使用示例**:
```tsx
// ProjectDetailPage.tsx

function ProjectDetailPage() {
  const [indexTaskId, setIndexTaskId] = useState<number | null>(null);
  const { progress, isComplete, error } = useTaskProgress(indexTaskId);

  const handleIndexCode = async () => {
    const response = await projectAPI.indexCode(projectId);
    setIndexTaskId(response.data.taskId);
  };

  return (
    <div>
      <BrutButton onClick={handleIndexCode}>
        索引代码
      </BrutButton>

      {progress && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 h-4 border-2 border-black">
            <div
              className="bg-brut-yellow h-full transition-all"
              style={{ width: `${progress.percent}%` }}
            />
          </div>
          <p className="mt-2 font-bold">{progress.message}</p>
          <p>{progress.percent}% ({progress.current}/{progress.total})</p>
        </div>
      )}

      {isComplete && (
        <p className="text-green-600 font-bold">✅ 索引完成！</p>
      )}
    </div>
  );
}
```

---

## 技术选型

### 服务间通信

| 方案 | 优点 | 缺点 | 选择 |
|-----|------|------|------|
| **RestTemplate** | 简单、同步调用 | 阻塞、性能一般 | ✅ **采用**(MVP阶段) |
| WebClient | 响应式、高性能 | 学习曲线陡 | ⏳ 后续优化 |
| Feign | 声明式、易用 | 需要额外依赖 | ⏳ 可选 |
| gRPC | 性能最好 | 复杂度高 | ❌ 过度设计 |

**结论**: Phase 6 使用 RestTemplate，后续可升级为 WebClient

### 异步任务

| 方案 | 优点 | 缺点 | 选择 |
|-----|------|------|------|
| **Celery** | 成熟稳定、功能强大 | Python专用 | ✅ **采用**(Python侧) |
| RabbitMQ | 跨语言、可靠 | 需额外中间件 | ⏳ 未来考虑 |
| Redis Queue | 轻量级 | 功能有限 | ❌ 不满足需求 |

**结论**: Python 使用 Celery + Redis

### 实时通信

| 方案 | 优点 | 缺点 | 选择 |
|-----|------|------|------|
| **WebSocket (STOMP)** | 双向通信、实时性好 | 需要额外配置 | ✅ **采用** |
| Server-Sent Events | 简单、单向推送 | 仅服务端推送 | ❌ 功能受限 |
| 轮询 | 简单 | 资源浪费 | ❌ 用户体验差 |

**结论**: 使用 Spring WebSocket + SockJS

### 代码静态分析

| 语言 | 工具 | 选择 |
|-----|------|------|
| Python | Pylint, Flake8 | ✅ **Pylint** |
| JavaScript/TypeScript | ESLint | ✅ **ESLint** |
| Java | Checkstyle, PMD | ✅ **Checkstyle** |

---

## 任务分解

### Week 1: 服务集成基础 (40小时)

#### Task 1.1: AgentClientService 实现 (8h)
- [ ] 创建 RestTemplate 配置
- [ ] 实现 indexRepository() 方法
- [ ] 实现 getIndexStatus() 方法
- [ ] 实现 askQuestion() 方法
- [ ] 添加重试机制 (RetryTemplate)
- [ ] 单元测试 (Mock Python服务)

#### Task 1.2: Java-Python 端到端集成测试 (8h)
- [ ] 启动 Python 服务
- [ ] Java 调用索引接口
- [ ] 验证状态查询
- [ ] 验证问答接口
- [ ] 异常场景测试
- [ ] 性能测试

#### Task 1.3: 统一错误处理 (6h)
- [ ] 定义 AgentServiceException
- [ ] 实现 AgentExceptionHandler
- [ ] 定义错误码枚举
- [ ] 添加日志记录
- [ ] 前端错误展示

#### Task 1.4: 项目创建自动触发索引 (8h)
- [ ] ProjectService 调用 AgentClient
- [ ] 创建 Task 记录
- [ ] 异步触发索引
- [ ] 状态更新逻辑
- [ ] 前端进度展示

#### Task 1.5: 集成测试和文档 (10h)
- [ ] 端到端集成测试
- [ ] API文档更新
- [ ] 部署文档更新
- [ ] 故障排查指南

### Week 2: 代码审查 Agent (40小时)

#### Task 2.1: 静态分析工具集成 (12h)
- [ ] Pylint 集成 (Python)
- [ ] ESLint 集成 (JavaScript/TypeScript)
- [ ] Checkstyle 集成 (Java)
- [ ] 统一输出格式
- [ ] 错误处理

#### Task 2.2: ReviewAgent 实现 (12h)
- [ ] 创建 ReviewAgent 类
- [ ] 实现 _static_analysis()
- [ ] 实现 _llm_review()
- [ ] 实现 _generate_report()
- [ ] 评分算法
- [ ] 单元测试

#### Task 2.3: 审查 API 实现 (8h)
- [ ] POST /api/v1/review/analyze
- [ ] GET /api/v1/review/result/{taskId}
- [ ] 数据模型定义
- [ ] 异常处理
- [ ] API 文档

#### Task 2.4: 前端审查功能 (8h)
- [ ] 审查按钮 UI
- [ ] 审查配置表单 (level选择)
- [ ] 审查报告展示组件
- [ ] Issue 详情展示
- [ ] 审查历史记录

### Week 3: 异步任务和实时通信 (40小时)

#### Task 3.1: Celery 配置和基础任务 (10h)
- [ ] Celery 安装和配置
- [ ] Redis Broker 配置
- [ ] index_repository_task 实现
- [ ] review_code_task 实现
- [ ] 任务监控 (Flower)

#### Task 3.2: 任务进度回调 (10h)
- [ ] CallbackTask 基类
- [ ] update_progress() 实现
- [ ] 进度存储 (Redis)
- [ ] Java 轮询逻辑
- [ ] 进度百分比计算

#### Task 3.3: WebSocket 实时推送 (12h)
- [ ] Spring WebSocket 配置
- [ ] TaskWebSocketController
- [ ] 任务状态推送
- [ ] 前端 WebSocket 连接
- [ ] useTaskProgress Hook
- [ ] 进度条组件

#### Task 3.4: 任务管理界面 (8h)
- [ ] 任务列表页面
- [ ] 任务状态筛选
- [ ] 任务详情查看
- [ ] 任务取消功能
- [ ] 任务重试功能

### Week 4: 性能优化和完善 (40小时)

#### Task 4.1: 性能优化 (12h)
- [ ] 索引批量处理优化
- [ ] 向量存储批量插入
- [ ] LLM 调用并发控制
- [ ] Redis 连接池优化
- [ ] 数据库查询优化

#### Task 4.2: 监控和日志 (8h)
- [ ] Celery 任务监控
- [ ] API 调用日志
- [ ] 性能指标收集
- [ ] 错误告警
- [ ] Grafana 面板 (可选)

#### Task 4.3: 集成测试 (10h)
- [ ] 端到端测试用例
- [ ] 性能测试
- [ ] 并发测试
- [ ] 故障恢复测试
- [ ] 测试报告

#### Task 4.4: 文档和演示 (10h)
- [ ] ADR 决策文档
- [ ] API 文档更新
- [ ] 部署文档
- [ ] 用户手册
- [ ] 演示视频录制

---

## 时间规划

### Gantt Chart

```
Week 1: 服务集成基础
├─ Day 1-2: AgentClientService 实现
├─ Day 2-3: 端到端集成测试
├─ Day 3-4: 统一错误处理
├─ Day 4-5: 项目创建触发索引
└─ Day 5:   集成测试和文档

Week 2: 代码审查 Agent
├─ Day 1-2: 静态分析工具集成
├─ Day 3-4: ReviewAgent 实现
├─ Day 4-5: 审查 API 实现
└─ Day 5:   前端审查功能

Week 3: 异步任务和实时通信
├─ Day 1-2: Celery 配置
├─ Day 3:   任务进度回调
├─ Day 4-5: WebSocket 实时推送
└─ Day 5:   任务管理界面

Week 4: 性能优化和完善
├─ Day 1-2: 性能优化
├─ Day 3:   监控和日志
├─ Day 4:   集成测试
└─ Day 5:   文档和演示
```

### 里程碑

| 里程碑 | 日期 | 交付物 |
|-------|------|-------|
| **M1: 服务集成完成** | Week 1 结束 | Java可成功调用Python所有接口 |
| **M2: 审查功能完成** | Week 2 结束 | 代码审查Agent完整实现 |
| **M3: 异步任务完成** | Week 3 结束 | WebSocket实时推送可用 |
| **M4: Phase 6 完成** | Week 4 结束 | 所有功能测试通过，文档完善 |

---

## 测试策略

### 单元测试

**Java 侧**:
```java
@Test
void testIndexRepository() {
    // Mock RestTemplate
    when(restTemplate.postForEntity(anyString(), any(), any()))
        .thenReturn(mockResponse);

    // 调用
    IndexResponse response = agentClient.indexRepository(1L, "/path/to/repo");

    // 验证
    assertThat(response.getProjectId()).isEqualTo(1L);
    assertThat(response.getStatus()).isEqualTo("COMPLETED");
}
```

**Python 侧**:
```python
@pytest.mark.asyncio
async def test_review_agent():
    # Arrange
    agent = ReviewAgent()
    mock_files = [create_mock_file("test.py")]

    # Act
    report = await agent.review_code(project_id=1, files=mock_files)

    # Assert
    assert report.score >= 0 and report.score <= 100
    assert len(report.issues) > 0
```

### 集成测试

**端到端流程**:
```python
def test_end_to_end_workflow():
    """测试完整流程: 创建项目 → 索引 → 问答 → 审查"""

    # 1. 创建项目 (Java)
    project_id = create_project("test-project")

    # 2. 触发索引 (Java → Python)
    task_id = trigger_index(project_id, "/path/to/repo")

    # 3. 等待索引完成
    wait_for_task_complete(task_id, timeout=60)

    # 4. 代码问答
    answer = ask_question(project_id, "项目的认证逻辑是怎样的？")
    assert "JWT" in answer

    # 5. 代码审查
    review_task = trigger_review(project_id)
    report = wait_for_review_complete(review_task)
    assert report.score > 0
```

### 性能测试

**指标**:
- 索引速度: ≥ 100 文件/分钟
- 审查速度: ≥ 50 文件/分钟
- API 响应时间: ≤ 200ms (P95)
- WebSocket 延迟: ≤ 500ms

---

## 已知风险

### 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| Python服务不稳定 | 高 | 中 | 添加重试、超时、降级策略 |
| LLM API限流 | 中 | 高 | 控制并发、添加重试、本地缓存 |
| WebSocket连接中断 | 中 | 中 | 自动重连、状态恢复 |
| 大仓库索引超时 | 高 | 中 | 分批处理、进度保存、断点续传 |
| Celery Worker崩溃 | 中 | 低 | 任务重试、监控告警 |

### 依赖风险

- OpenAI API 可用性
- Redis 服务稳定性
- ChromaDB 存储容量

### 缓解策略

1. **降级方案**: LLM不可用时，只使用静态分析
2. **重试机制**: 所有外部调用都添加重试
3. **超时控制**: 防止长时间阻塞
4. **监控告警**: 及时发现问题
5. **优雅降级**: 部分功能失败不影响整体

---

## 成功标准

### 功能完整性
- ✅ Java可成功调用Python所有接口
- ✅ 创建项目自动触发索引
- ✅ WebSocket实时推送进度
- ✅ 代码审查生成完整报告
- ✅ 任务可取消和重试

### 质量标准
- ✅ 单元测试覆盖率 ≥ 80%
- ✅ 集成测试通过率 100%
- ✅ 性能测试达标
- ✅ 无P0/P1级别Bug

### 文档完整性
- ✅ ADR决策文档
- ✅ API文档更新
- ✅ 部署文档
- ✅ 用户手册
- ✅ 演示视频

---

## 参考资料

### 技术文档
- [Spring Boot RestTemplate](https://docs.spring.io/spring-boot/docs/current/reference/html/io.html#io.rest-client)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Spring WebSocket](https://docs.spring.io/spring-framework/reference/web/websocket.html)
- [ESLint User Guide](https://eslint.org/docs/user-guide/)

### 最佳实践
- [Microservices Communication Patterns](https://microservices.io/patterns/communication-style/messaging.html)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)
- [Async Task Processing](https://www.fullstackpython.com/task-queues.html)

---

**文档维护**: 随着开发推进持续更新
**责任人**: 开发团队
**审核周期**: 每周 Review
