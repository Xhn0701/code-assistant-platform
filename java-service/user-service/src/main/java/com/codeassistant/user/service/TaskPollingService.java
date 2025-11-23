package com.codeassistant.user.service;

import com.codeassistant.user.client.AgentClientService;
import com.codeassistant.user.client.dto.TaskStatusResponse;
import com.codeassistant.user.dto.TaskProgressDTO;
import com.codeassistant.user.entity.AsyncTask;
import com.codeassistant.user.mapper.AsyncTaskMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 任务轮询服务
 *
 * 功能:
 * 1. 定时轮询正在运行的任务
 * 2. 从 Python 服务获取最新进度
 * 3. 通过 WebSocket 实时推送给前端
 *
 * ⭐⭐⭐⭐⭐ 面试核心竞争力!
 *
 * 架构说明:
 * 前端 <-- WebSocket --> Java <-- HTTP轮询 --> Python
 *
 * 为什么这样设计?
 * - Python 是 HTTP API,不支持主动推送
 * - Java 在中间层做协议转换
 * - 前端统一使用 WebSocket,体验一致
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class TaskPollingService {

    private final AsyncTaskMapper taskMapper;
    private final AgentClientService agentClient;
    private final WebSocketService webSocketService;

    /**
     * 每2秒轮询一次正在运行的任务
     * 从Python服务获取最新进度,推送到前端
     */
    @Scheduled(fixedDelay = 2000)
    public void pollRunningTasks() {
        List<AsyncTask> runningTasks = taskMapper.findRunningTasks();

        if (runningTasks.isEmpty()) {
            return;  // 无运行中任务,跳过
        }

        log.debug("轮询 {} 个运行中的任务", runningTasks.size());

        for (AsyncTask task : runningTasks) {
            try {
                // 调用 Python 服务查询任务状态
                TaskStatusResponse status = agentClient.getTaskStatus(task.getCeleryTaskId());

                // 更新本地任务状态
                task.setProgress(status.getProgress());
                task.setMessage(status.getMessage());

                if ("SUCCESS".equals(status.getState())) {
                    // 任务成功完成
                    task.setStatus(AsyncTask.TaskStatus.COMPLETED);
                    task.setResult(status.getResult());

                    // 推送完成通知
                    webSocketService.sendTaskComplete(task.getId(), status.getResult());

                    log.info("任务完成: taskId={}, celeryTaskId={}",
                        task.getId(), task.getCeleryTaskId());

                } else if ("FAILURE".equals(status.getState())) {
                    // 任务失败
                    task.setStatus(AsyncTask.TaskStatus.FAILED);
                    task.setErrorMessage(status.getError());

                    // 推送失败通知
                    webSocketService.sendTaskFailed(task.getId(), status.getError());

                    log.warn("任务失败: taskId={}, error={}",
                        task.getId(), status.getError());

                } else {
                    // 任务进行中
                    if ("PENDING".equals(task.getStatus())) {
                        task.setStatus(AsyncTask.TaskStatus.RUNNING);
                    }

                    // 推送进度更新
                    TaskProgressDTO progress = TaskProgressDTO.builder()
                        .taskId(task.getId())
                        .status(status.getState())
                        .progress(status.getProgress())
                        .message(status.getMessage())
                        .timestamp(System.currentTimeMillis())
                        .build();

                    webSocketService.sendTaskProgress(task.getId(), progress);

                    log.debug("任务进行中: taskId={}, progress={}%",
                        task.getId(), status.getProgress());
                }

                // 保存任务状态
                taskMapper.updateById(task);

            } catch (Exception e) {
                log.error("轮询任务状态失败: taskId={}, error={}",
                    task.getId(), e.getMessage());
            }
        }
    }
}
