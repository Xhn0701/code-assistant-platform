package com.codeassistant.user.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.codeassistant.user.common.Result;
import com.codeassistant.user.dto.ChatDtos;
import com.codeassistant.user.security.SecurityUtils;
import com.codeassistant.user.service.ChatService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.List;

/**
 * 对话与消息接口
 *
 * 提供基础的创建对话、发送消息、查询历史记录能力。
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/chat")
@RequiredArgsConstructor
@Tag(name = "对话系统", description = "对话与消息管理接口")
@SecurityRequirement(name = "bearerAuth")
public class ChatController {

    private final ChatService chatService;

    /**
     * 创建新对话
     */
    @PostMapping("/conversations")
    @Operation(summary = "创建对话", description = "在指定项目下创建一个新的对话会话")
    public Result<ChatDtos.ConversationResponse> createConversation(
            @Valid @RequestBody ChatDtos.CreateConversationRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        log.info("Creating conversation for user: {}, project: {}", userId, request.getProjectId());
        ChatDtos.ConversationResponse response = chatService.createConversation(userId, request);
        return Result.success(response);
    }

    /**
     * 获取项目下的对话列表
     */
    @GetMapping("/conversations/{projectId}")
    @Operation(summary = "获取对话列表", description = "按项目获取当前用户的对话列表")
    public Result<List<ChatDtos.ConversationResponse>> getConversations(
            @Parameter(description = "项目ID") @PathVariable Long projectId) {
        Long userId = SecurityUtils.getCurrentUserId();
        List<ChatDtos.ConversationResponse> list = chatService.getConversationsByProject(userId, projectId);
        return Result.success(list);
    }

    /**
     * 在对话中发送消息
     */
    @PostMapping("/{conversationId}/messages")
    @Operation(summary = "发送消息", description = "在指定对话中发送一条用户消息")
    public Result<ChatDtos.MessageResponse> sendMessage(
            @Parameter(description = "对话ID") @PathVariable String conversationId,
            @Valid @RequestBody ChatDtos.SendMessageRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        ChatDtos.MessageResponse response = chatService.sendMessage(userId, conversationId, request);
        return Result.success(response);
    }

    /**
     * 获取对话历史消息（分页）
     */
    @GetMapping("/{conversationId}/messages/paged")
    @Operation(summary = "获取消息历史（分页）", description = "分页获取指定对话下的消息列表")
    public Result<Page<ChatDtos.MessageResponse>> getMessagesPaged(
            @Parameter(description = "对话ID") @PathVariable String conversationId,
            @Parameter(description = "页码（从1开始）") @RequestParam(defaultValue = "1") Integer pageNum,
            @Parameter(description = "每页大小") @RequestParam(defaultValue = "50") Integer pageSize) {
        Long userId = SecurityUtils.getCurrentUserId();
        Page<ChatDtos.MessageResponse> page = chatService.getMessagesPaged(userId, conversationId, pageNum, pageSize);
        return Result.success(page);
    }

    /**
     * 获取对话历史消息（全部，不分页）
     */
    @GetMapping("/{conversationId}/messages")
    @Operation(summary = "获取消息历史（全部）", description = "获取指定对话下的所有消息列表（不分页，谨慎使用）")
    public Result<List<ChatDtos.MessageResponse>> getMessages(
            @Parameter(description = "对话ID") @PathVariable String conversationId) {
        Long userId = SecurityUtils.getCurrentUserId();
        List<ChatDtos.MessageResponse> list = chatService.getMessages(userId, conversationId);
        return Result.success(list);
    }
}

