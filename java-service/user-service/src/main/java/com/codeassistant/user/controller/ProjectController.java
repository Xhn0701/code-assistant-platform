package com.codeassistant.user.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.codeassistant.user.common.Result;
import com.codeassistant.user.dto.CreateProjectRequest;
import com.codeassistant.user.dto.ProjectResponse;
import com.codeassistant.user.dto.UpdateProjectRequest;
import com.codeassistant.user.security.SecurityUtils;
import com.codeassistant.user.service.ProjectService;
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
 * 项目管理控制器
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/projects")
@RequiredArgsConstructor
@Tag(name = "项目管理", description = "项目CRUD接口")
@SecurityRequirement(name = "bearerAuth")
public class ProjectController {

    private final ProjectService projectService;

    /**
     * 创建项目
     */
    @PostMapping
    @Operation(summary = "创建项目", description = "为当前用户创建一个新项目")
    public Result<ProjectResponse> createProject(
            @Valid @RequestBody CreateProjectRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        log.info("Creating project for user: {}", userId);
        ProjectResponse response = projectService.createProject(userId, request);
        return Result.success(response);
    }

    /**
     * 获取项目详情
     */
    @GetMapping("/{id}")
    @Operation(summary = "获取项目详情", description = "根据项目ID获取项目详细信息")
    public Result<ProjectResponse> getProject(
            @Parameter(description = "项目ID") @PathVariable Long id) {
        Long userId = SecurityUtils.getCurrentUserId();
        ProjectResponse response = projectService.getProject(userId, id);
        return Result.success(response);
    }

    /**
     * 获取用户的所有项目
     */
    @GetMapping
    @Operation(summary = "获取项目列表", description = "获取当前用户的所有项目")
    public Result<List<ProjectResponse>> getUserProjects() {
        Long userId = SecurityUtils.getCurrentUserId();
        List<ProjectResponse> projects = projectService.getUserProjects(userId);
        return Result.success(projects);
    }

    /**
     * 获取用户的项目列表（分页）
     */
    @GetMapping("/paged")
    @Operation(summary = "获取项目列表（分页）", description = "分页获取当前用户的项目")
    public Result<Page<ProjectResponse>> getUserProjectsPaged(
            @Parameter(description = "页码，从1开始") @RequestParam(defaultValue = "1") int page,
            @Parameter(description = "每页大小") @RequestParam(defaultValue = "10") int size) {
        Long userId = SecurityUtils.getCurrentUserId();
        Page<ProjectResponse> projectPage = projectService.getUserProjectsPaged(userId, page, size);
        return Result.success(projectPage);
    }

    /**
     * 更新项目
     */
    @PutMapping("/{id}")
    @Operation(summary = "更新项目", description = "更新项目信息")
    public Result<ProjectResponse> updateProject(
            @Parameter(description = "项目ID") @PathVariable Long id,
            @Valid @RequestBody UpdateProjectRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        log.info("Updating project: {} for user: {}", id, userId);
        ProjectResponse response = projectService.updateProject(userId, id, request);
        return Result.success(response);
    }

    /**
     * 删除项目
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "删除项目", description = "删除指定项目（逻辑删除）")
    public Result<Void> deleteProject(
            @Parameter(description = "项目ID") @PathVariable Long id) {
        Long userId = SecurityUtils.getCurrentUserId();
        log.info("Deleting project: {} for user: {}", id, userId);
        projectService.deleteProject(userId, id);
        return Result.success();
    }

    /**
     * 统计用户项目数量
     */
    @GetMapping("/count")
    @Operation(summary = "统计项目数量", description = "获取当前用户的项目总数")
    public Result<Long> countProjects() {
        Long userId = SecurityUtils.getCurrentUserId();
        long count = projectService.countUserProjects(userId);
        return Result.success(count);
    }

    /**
     * 触发代码审查
     */
    @PostMapping("/{id}/review")
    @Operation(summary = "触发代码审查", description = "对项目进行代码审查")
    public Result<com.codeassistant.user.client.dto.ReviewResponse> reviewCode(
            @Parameter(description = "项目ID") @PathVariable Long id,
            @RequestBody(required = false) ReviewCodeRequest request) {
        Long userId = SecurityUtils.getCurrentUserId();
        String level = request != null && request.getLevel() != null ? request.getLevel() : "standard";
        log.info("Starting code review for project: {}, level: {}", id, level);
        var response = projectService.reviewCode(userId, id, level);
        return Result.success(response);
    }

    /**
     * 获取审查结果
     */
    @GetMapping("/{id}/review/{taskId}")
    @Operation(summary = "获取审查结果", description = "根据任务ID获取审查结果")
    public Result<Object> getReviewResult(
            @Parameter(description = "项目ID") @PathVariable Long id,
            @Parameter(description = "任务ID") @PathVariable String taskId) {
        Long userId = SecurityUtils.getCurrentUserId();
        log.info("Getting review result for project: {}, taskId: {}", id, taskId);
        Object result = projectService.getReviewResult(userId, id, taskId);
        return Result.success(result);
    }

    /**
     * 审查请求DTO (内部类)
     */
    @lombok.Data
    public static class ReviewCodeRequest {
        private String level; // quick, standard, full
    }
}
