package com.codeassistant.user.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 代码审查响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewResponse {
    /**
     * 任务ID (Celery task ID)
     */
    private String taskId;

    /**
     * 任务状态: PENDING, RUNNING, COMPLETED, FAILED
     */
    private String status;

    /**
     * 预估耗时(秒)
     */
    private Integer estimatedTime;

    /**
     * 消息
     */
    private String message;
}
