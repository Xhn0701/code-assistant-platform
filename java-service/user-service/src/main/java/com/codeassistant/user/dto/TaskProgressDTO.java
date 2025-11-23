package com.codeassistant.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 任务进度 DTO
 *
 * 用于 WebSocket 实时推送任务进度
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskProgressDTO {
    /**
     * 任务ID
     */
    private Long taskId;

    /**
     * 任务状态: PENDING, RUNNING, COMPLETED, FAILED
     */
    private String status;

    /**
     * 进度百分比 (0-100)
     */
    private Integer progress;

    /**
     * 进度描述信息
     */
    private String message;

    /**
     * 任务结果 (完成时)
     */
    private Object result;

    /**
     * 时间戳
     */
    private Long timestamp;
}
