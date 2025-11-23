package com.codeassistant.user.service;

import com.codeassistant.user.dto.TaskProgressDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

/**
 * WebSocket 消息推送服务
 *
 * 功能:
 * 1. 推送任务进度更新
 * 2. 推送任务完成通知
 * 3. 推送任务失败通知
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class WebSocketService {

    private final SimpMessagingTemplate messagingTemplate;

    /**
     * 推送任务进度
     *
     * @param taskId 任务ID
     * @param progress 进度对象
     */
    public void sendTaskProgress(Long taskId, TaskProgressDTO progress) {
        String destination = "/topic/task/" + taskId;

        log.debug("推送任务进度到 {}: {}%", destination, progress.getProgress());

        messagingTemplate.convertAndSend(destination, progress);
    }

    /**
     * 推送任务完成通知
     *
     * @param taskId 任务ID
     * @param result 任务结果
     */
    public void sendTaskComplete(Long taskId, Object result) {
        TaskProgressDTO progress = TaskProgressDTO.builder()
            .taskId(taskId)
            .status("COMPLETED")
            .progress(100)
            .message("任务完成")
            .result(result)
            .timestamp(System.currentTimeMillis())
            .build();

        sendTaskProgress(taskId, progress);
        log.info("任务完成通知已推送: taskId={}", taskId);
    }

    /**
     * 推送任务失败通知
     *
     * @param taskId 任务ID
     * @param error 错误信息
     */
    public void sendTaskFailed(Long taskId, String error) {
        TaskProgressDTO progress = TaskProgressDTO.builder()
            .taskId(taskId)
            .status("FAILED")
            .message("任务失败: " + error)
            .timestamp(System.currentTimeMillis())
            .build();

        sendTaskProgress(taskId, progress);
        log.warn("任务失败通知已推送: taskId={}, error={}", taskId, error);
    }
}
