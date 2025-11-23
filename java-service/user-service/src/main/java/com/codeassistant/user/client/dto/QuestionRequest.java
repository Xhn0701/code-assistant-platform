package com.codeassistant.user.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 代码问答请求 DTO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QuestionRequest {
    /**
     * 项目ID
     */
    private Long projectId;

    /**
     * 用户问题
     */
    private String question;

    /**
     * 会话ID (用于多轮对话)
     */
    private Long conversationId;
}
