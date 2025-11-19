package com.codeassistant.user.dto;

import com.codeassistant.user.entity.Conversation;
import com.codeassistant.user.entity.Message;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;

/**
 * 对话与消息相关 DTO/VO
 */
@Slf4j
public class ChatDtos {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    @Data
    public static class CreateConversationRequest {

        /**
         * 项目ID
         */
        @NotNull(message = "项目ID不能为空")
        private Long projectId;

        /**
         * 对话标题（可选）
         */
        private String title;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ConversationResponse {

        private String id;
        private Long projectId;
        private Long userId;
        private String title;
        private LocalDateTime createdAt;
        private LocalDateTime updatedAt;

        public static ConversationResponse fromEntity(Conversation conversation) {
            if (conversation == null) {
                return null;
            }
            return ConversationResponse.builder()
                    .id(conversation.getId())
                    .projectId(conversation.getProjectId())
                    .userId(conversation.getUserId())
                    .title(conversation.getTitle())
                    .createdAt(conversation.getCreatedAt())
                    .updatedAt(conversation.getUpdatedAt())
                    .build();
        }
    }

    @Data
    public static class SendMessageRequest {

        /**
         * 消息内容
         */
        @NotBlank(message = "消息内容不能为空")
        private String content;
    }

    /**
     * 代码引用 DTO
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CodeReferenceDto {
        private String filePath;
        private Integer startLine;
        private Integer endLine;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MessageResponse {

        private Long id;
        private String conversationId;
        private String role;
        private String content;
        private List<CodeReferenceDto> sources;  // 类型化：List<CodeReferenceDto> 而非 String
        private LocalDateTime createdAt;

        public static MessageResponse fromEntity(Message message) {
            if (message == null) {
                return null;
            }
            
            // 反序列化 JSON sources
            List<CodeReferenceDto> sources = null;
            if (message.getSources() != null && !message.getSources().trim().isEmpty()) {
                try {
                    sources = OBJECT_MAPPER.readValue(
                        message.getSources(),
                        new TypeReference<List<CodeReferenceDto>>() {}
                    );
                } catch (JsonProcessingException e) {
                    log.warn("Failed to parse sources JSON for message {}: {}", 
                            message.getId(), e.getMessage());
                    sources = Collections.emptyList();
                }
            }
            
            return MessageResponse.builder()
                    .id(message.getId())
                    .conversationId(message.getConversationId())
                    .role(message.getRole())
                    .content(message.getContent())
                    .sources(sources)
                    .createdAt(message.getCreatedAt())
                    .build();
        }
    }
}

