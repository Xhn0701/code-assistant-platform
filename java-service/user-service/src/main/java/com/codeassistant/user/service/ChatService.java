package com.codeassistant.user.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.codeassistant.user.dto.ChatDtos;
import com.codeassistant.user.entity.Conversation;
import com.codeassistant.user.entity.Message;

import java.util.List;

/**
 * 对话与消息服务
 *
 * 负责管理会话及其消息的基础业务逻辑。
 */
public interface ChatService {

    /**
     * 创建新对话
     *
     * @param userId 当前用户ID
     * @param request 创建对话请求
     * @return 对话响应
     */
    ChatDtos.ConversationResponse createConversation(Long userId, ChatDtos.CreateConversationRequest request);

    /**
     * 获取指定项目下的对话列表（当前用户）
     *
     * @param userId 当前用户ID
     * @param projectId 项目ID
     * @return 对话列表
     */
    List<ChatDtos.ConversationResponse> getConversationsByProject(Long userId, Long projectId);

    /**
     * 在指定对话中发送消息
     *
     * @param userId 当前用户ID
     * @param conversationId 对话ID
     * @param request 发送消息请求
     * @return 消息响应
     */
    ChatDtos.MessageResponse sendMessage(Long userId, String conversationId, ChatDtos.SendMessageRequest request);

    /**
     * 获取对话的消息历史（分页）
     *
     * @param userId 当前用户ID
     * @param conversationId 对话ID
     * @param pageNum 页码（从1开始）
     * @param pageSize 每页大小
     * @return 消息分页响应
     */
    Page<ChatDtos.MessageResponse> getMessagesPaged(Long userId, String conversationId, Integer pageNum, Integer pageSize);

    /**
     * 获取对话的消息历史（全部，不分页）
     *
     * @param userId 当前用户ID
     * @param conversationId 对话ID
     * @return 消息响应列表
     */
    List<ChatDtos.MessageResponse> getMessages(Long userId, String conversationId);

    /**
     * 获取对话实体（内部使用）
     */
    Conversation getConversationEntity(Long userId, String conversationId);

    /**
     * 获取消息实体（内部或后续扩展使用）
     */
    Message getMessageEntity(Long userId, Long messageId);
}

