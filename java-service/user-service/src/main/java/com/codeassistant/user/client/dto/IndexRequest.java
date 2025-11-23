package com.codeassistant.user.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 代码索引请求 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IndexRequest {
    /**
     * 项目ID
     */
    private Long projectId;

    /**
     * 代码仓库路径 (对应 Python API 的 repositoryUrl)
     */
    private String repositoryUrl;
}
