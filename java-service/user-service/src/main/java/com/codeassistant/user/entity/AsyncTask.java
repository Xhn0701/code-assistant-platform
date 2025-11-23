package com.codeassistant.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 异步任务实体
 *
 * 用于记录后台运行的异步任务 (代码索引、代码审查等)
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("async_tasks")
public class AsyncTask {

    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 关联的项目ID
     */
    private Long projectId;

    /**
     * 任务类型: INDEX(索引), REVIEW(审查), CHAT(问答)
     */
    private String taskType;

    /**
     * Celery任务ID
     */
    private String celeryTaskId;

    /**
     * 任务状态: PENDING, RUNNING, COMPLETED, FAILED
     */
    private String status;

    /**
     * 进度百分比 (0-100)
     */
    private Integer progress;

    /**
     * 当前进度描述
     */
    private String message;

    /**
     * 预估耗时 (秒)
     */
    private Integer estimatedTime;

    /**
     * 实际耗时 (秒)
     */
    private Integer actualTime;

    /**
     * 任务结果 (JSON格式)
     */
    @TableField(typeHandler = com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler.class)
    private Object result;

    /**
     * 错误信息
     */
    private String errorMessage;

    /**
     * 创建时间
     */
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /**
     * 逻辑删除标记
     */
    @TableLogic
    private Integer deleted;

    /**
     * 任务类型枚举
     */
    public static class TaskType {
        public static final String INDEX = "INDEX";
        public static final String REVIEW = "REVIEW";
        public static final String CHAT = "CHAT";
    }

    /**
     * 任务状态枚举
     */
    public static class TaskStatus {
        public static final String PENDING = "PENDING";
        public static final String RUNNING = "RUNNING";
        public static final String COMPLETED = "COMPLETED";
        public static final String FAILED = "FAILED";
    }
}
