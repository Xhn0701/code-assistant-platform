package com.codeassistant.user.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.codeassistant.user.common.BusinessException;
import com.codeassistant.user.common.ResultCode;
import com.codeassistant.user.dto.ChatDtos;
import com.codeassistant.user.entity.Conversation;
import com.codeassistant.user.entity.Message;
import com.codeassistant.user.mapper.ConversationMapper;
import com.codeassistant.user.mapper.MessageMapper;
import com.codeassistant.user.service.ChatService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 对话与消息服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ChatServiceImpl implements ChatService {

    private final ConversationMapper conversationMapper;
    private final MessageMapper messageMapper;

    @Override
    @Transactional
    public ChatDtos.ConversationResponse createConversation(Long userId, ChatDtos.CreateConversationRequest request) {
        log.info("Creating conversation for user: {}, project: {}", userId, request.getProjectId());

        Conversation conversation = Conversation.builder()
                .projectId(request.getProjectId())
                .userId(userId)
                .title(request.getTitle())
                .deleted(0)
                // createdAt 和 updatedAt 由 MetaObjectHandler 自动填充
                .build();

        conversationMapper.insert(conversation);
        return ChatDtos.ConversationResponse.fromEntity(conversation);
    }

    @Override
    public List<ChatDtos.ConversationResponse> getConversationsByProject(Long userId, Long projectId) {
        log.info("Fetching conversations for user: {}, project: {}", userId, projectId);
        List<Conversation> conversations = conversationMapper.findByProjectIdAndUserId(projectId, userId);
        return conversations.stream()
                .map(ChatDtos.ConversationResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional
    public ChatDtos.MessageResponse sendMessage(Long userId, String conversationId, ChatDtos.SendMessageRequest request) {
        Conversation conversation = getConversationEntity(userId, conversationId);

        Message message = Message.builder()
                .conversationId(conversation.getId())
                .role(Message.Role.USER)
                .content(request.getContent())
                .sources(null)
                .deleted(0)
                // createdAt 和 updatedAt 由 MetaObjectHandler 自动填充
                .build();

        messageMapper.insert(message);
        return ChatDtos.MessageResponse.fromEntity(message);
    }

    @Override
    public Page<ChatDtos.MessageResponse> getMessagesPaged(Long userId, String conversationId, Integer pageNum, Integer pageSize) {
        Conversation conversation = getConversationEntity(userId, conversationId);
        
        // 创建分页对象
        Page<Message> messagePage = new Page<>(pageNum, pageSize);
        
        // 构建查询条件
        LambdaQueryWrapper<Message> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Message::getConversationId, conversation.getId())
               .eq(Message::getDeleted, 0)
               .orderByAsc(Message::getCreatedAt);
        
        // 执行分页查询
        messageMapper.selectPage(messagePage, wrapper);
        
        // 转换为 DTO 分页对象
        Page<ChatDtos.MessageResponse> responsePage = new Page<>(messagePage.getCurrent(), messagePage.getSize(), messagePage.getTotal());
        responsePage.setRecords(
            messagePage.getRecords().stream()
                .map(ChatDtos.MessageResponse::fromEntity)
                .collect(Collectors.toList())
        );
        
        return responsePage;
    }

    @Override
    public List<ChatDtos.MessageResponse> getMessages(Long userId, String conversationId) {
        Conversation conversation = getConversationEntity(userId, conversationId);
        List<Message> messages = messageMapper.findByConversationId(conversation.getId());
        return messages.stream()
                .map(ChatDtos.MessageResponse::fromEntity)
                .collect(Collectors.toList());
    }

    @Override
    public Conversation getConversationEntity(Long userId, String conversationId) {
        Conversation conversation = conversationMapper.selectById(conversationId);
        // @TableLogic 已自动过滤 deleted=1 的记录，selectById 返回 null 表示不存在或已删除
        if (conversation == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "对话不存在");
        }
        if (!conversation.getUserId().equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权访问该对话");
        }
        return conversation;
    }

    @Override
    public Message getMessageEntity(Long userId, Long messageId) {
        Message message = messageMapper.selectById(messageId);
        // @TableLogic 已自动过滤 deleted=1 的记录
        if (message == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "消息不存在");
        }
        // 校验所属对话是否属于当前用户
        Conversation conversation = conversationMapper.selectById(message.getConversationId());
        if (conversation == null) {
            throw new BusinessException(ResultCode.NOT_FOUND, "对话不存在");
        }
        if (!conversation.getUserId().equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权访问该消息");
        }
        return message;
    }
}

