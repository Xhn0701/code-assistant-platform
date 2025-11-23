package com.codeassistant.user.controller;

import com.codeassistant.user.common.Result;
import com.codeassistant.user.dto.IndexCallbackRequest;
import com.codeassistant.user.service.ProjectService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * 回调接口控制器
 * 接收 Agent 服务的回调通知
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/callback")
@RequiredArgsConstructor
@Tag(name = "回调接口", description = "接收 Agent 服务的回调通知")
public class CallbackController {

    private final ProjectService projectService;

    /**
     * 索引状态回调
     * Python Agent 服务在索引完成后调用此接口更新项目状态
     */
    @PostMapping("/index-status")
    @Operation(summary = "索引状态回调", description = "Agent 服务索引完成后调用")
    public Result<Void> updateIndexStatus(@Valid @RequestBody IndexCallbackRequest request) {
        log.info("Received index callback: projectId={}, status={}, totalFiles={}",
            request.getProjectId(), request.getStatus(), request.getTotalFiles());

        projectService.handleIndexCallback(request);

        return Result.success();
    }
}
