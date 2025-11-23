package com.codeassistant.user.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 代码问答响应 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QuestionResponse {
    /**
     * AI回答内容
     */
    private String answer;

    /**
     * 相关代码引用
     */
    private List<CodeReference> references;

    /**
     * 置信度 (0.0-1.0)
     */
    private Double confidence;

    /**
     * 代码引用信息
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CodeReference {
        /**
         * 文件路径
         */
        private String filePath;

        /**
         * 起始行号
         */
        private Integer startLine;

        /**
         * 结束行号
         */
        private Integer endLine;

        /**
         * 代码片段
         */
        private String content;

        /**
         * 相似度得分
         */
        private Double score;
    }
}
