package com.codeassistant.user.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 代码索引响应 DTO
 * 对应 Python API 的 IndexRepositoryResult
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IndexResponse {
    /**
     * 项目ID
     */
    private Long projectId;

    /**
     * 索引状态: PENDING, INDEXING, COMPLETED, FAILED
     */
    private String status;

    /**
     * 扫描到的文件总数
     */
    private Integer totalFiles;

    /**
     * 已索引的文件数
     */
    private Integer indexedFiles;

    /**
     * 失败原因（仅 FAILED 时有值）
     */
    private String errorMessage;
}
