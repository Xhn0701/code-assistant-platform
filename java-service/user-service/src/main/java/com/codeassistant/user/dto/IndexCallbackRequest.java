package com.codeassistant.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;

/**
 * 索引回调请求 DTO
 * Python Agent 服务索引完成后回调使用
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IndexCallbackRequest {

    /**
     * 项目 ID
     */
    @NotNull(message = "项目 ID 不能为空")
    private Long projectId;

    /**
     * 索引状态
     * COMPLETED - 索引完成
     * FAILED - 索引失败
     */
    @NotBlank(message = "索引状态不能为空")
    private String status;

    /**
     * 总文件数
     */
    private Integer totalFiles;

    /**
     * 已索引文件数
     */
    private Integer indexedFiles;

    /**
     * 主要编程语言
     */
    private String language;

    /**
     * 错误消息 (如果失败)
     */
    private String errorMessage;

    /**
     * 任务 ID
     */
    private String taskId;
}
