package com.codeassistant.user.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 代码审查请求 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewRequest {
    /**
     * 项目ID
     */
    private Long projectId;

    /**
     * 项目路径 (Agent 服务需要此路径进行代码审查)
     */
    private String projectPath;

    /**
     * 指定审查的文件列表 (为null则审查全部文件)
     */
    private List<String> files;

    /**
     * 审查深度级别:
     * - quick: 仅静态分析
     * - standard: 静态分析 + LLM审查核心文件
     * - full: 静态分析 + LLM审查所有文件
     */
    private String level;
}
