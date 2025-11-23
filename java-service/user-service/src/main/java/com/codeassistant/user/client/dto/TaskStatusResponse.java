package com.codeassistant.user.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 任务状态查询响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskStatusResponse {
    /**
     * 任务状态: PENDING, PROGRESS, SUCCESS, FAILURE
     */
    private String state;

    /**
     * 进度百分比 (0-100)
     */
    private Integer progress;

    /**
     * 当前进度描述
     */
    private String message;

    /**
     * 任务结果 (SUCCESS时)
     */
    private Object result;

    /**
     * 错误信息 (FAILURE时)
     */
    private String error;
}
