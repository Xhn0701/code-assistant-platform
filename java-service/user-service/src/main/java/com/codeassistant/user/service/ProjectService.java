package com.codeassistant.user.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.codeassistant.user.common.BusinessException;
import com.codeassistant.user.common.ResultCode;
import com.codeassistant.user.dto.CreateProjectRequest;
import com.codeassistant.user.dto.ProjectResponse;
import com.codeassistant.user.dto.UpdateProjectRequest;
import com.codeassistant.user.entity.AsyncTask;
import com.codeassistant.user.entity.Project;
import com.codeassistant.user.mapper.AsyncTaskMapper;
import com.codeassistant.user.mapper.ProjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 项目服务类
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ProjectService {

    private final ProjectMapper projectMapper;
    private final AsyncTaskMapper asyncTaskMapper;
    private final com.codeassistant.user.client.AgentClientService agentClient;
    private final GitService gitService;

    /**
     * 创建项目
     * 完整流程: 创建项目 → 克隆/验证代码路径 → 自动触发索引
     *
     * @param userId 用户ID
     * @param request 创建请求
     * @return 项目响应
     */
    @Transactional
    public ProjectResponse createProject(Long userId, CreateProjectRequest request) {
        log.info("Creating project for user: {}, name: {}", userId, request.getName());

        // 1. 检查项目名称是否已存在
        Project existingProject = projectMapper.findByUserIdAndName(userId, request.getName());
        if (existingProject != null) {
            throw new BusinessException(ResultCode.PROJECT_NAME_EXISTS);
        }

        // 2. 确定仓库类型
        String repositoryType = determineRepositoryType(request);

        // 3. 构建项目实体 (先不设置 localPath)
        Project project = Project.builder()
                .userId(userId)
                .name(request.getName())
                .description(request.getDescription())
                .repositoryUrl(request.getRepositoryUrl())
                .repositoryType(repositoryType)
                .status(Project.Status.CREATED)
                .indexStatus(Project.IndexStatus.PENDING)
                .totalFiles(0)
                .indexedFiles(0)
                .deleted(0)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        // 4. 保存项目 (获取自动生成的 ID)
        projectMapper.insert(project);
        log.info("Project created with ID: {}", project.getId());

        try {
            // 5. 处理代码路径
            String localPath = prepareProjectPath(project, request);
            project.setLocalPath(localPath);

            // 更新项目本地路径
            projectMapper.updateById(project);
            log.info("Project local path set: {}", localPath);

            // 6. 自动触发索引
            triggerAutoIndex(project);

        } catch (Exception e) {
            log.error("Failed to prepare project or trigger indexing: {}", e.getMessage(), e);
            // 更新项目状态为 ERROR
            project.setStatus(Project.Status.ERROR);
            project.setIndexStatus(Project.IndexStatus.FAILED);
            projectMapper.updateById(project);

            throw new BusinessException("项目创建失败: " + e.getMessage());
        }

        return ProjectResponse.fromEntity(project);
    }

    /**
     * 准备项目路径 (克隆或验证本地路径)
     */
    private String prepareProjectPath(Project project, CreateProjectRequest request) {
        String repositoryType = project.getRepositoryType();

        // 情况1: LOCAL 类型 - 验证本地路径
        if (Project.RepositoryType.LOCAL.equals(repositoryType)) {
            String localPath = request.getLocalPath();
            if (!StringUtils.hasText(localPath)) {
                throw new BusinessException("LOCAL 类型项目必须提供本地路径");
            }

            if (!gitService.validateLocalPath(localPath)) {
                throw new BusinessException("本地路径无效或不存在: " + localPath);
            }

            log.info("Local project path validated: {}", localPath);
            return localPath;
        }

        // 情况2: 远程仓库 (GITHUB, GITLAB, BITBUCKET)
        String repositoryUrl = project.getRepositoryUrl();
        if (!StringUtils.hasText(repositoryUrl)) {
            throw new BusinessException("远程仓库项目必须提供仓库 URL");
        }

        // 如果用户指定了本地路径,优先使用
        if (StringUtils.hasText(request.getLocalPath())) {
            log.info("Using user-specified local path: {}", request.getLocalPath());
            return request.getLocalPath();
        }

        // 否则克隆到默认位置
        log.info("Cloning repository: {} for project {}", repositoryUrl, project.getId());
        return gitService.cloneRepository(repositoryUrl, project.getId());
    }

    /**
     * 自动触发索引
     */
    private void triggerAutoIndex(Project project) {
        log.info("Triggering auto-index for project: {}", project.getId());

        // 更新状态为 INDEXING
        project.setStatus(Project.Status.INDEXING);
        project.setIndexStatus(Project.IndexStatus.INDEXING);
        projectMapper.updateById(project);

        try {
            // 调用 Agent 服务进行索引（同步操作）
            com.codeassistant.user.client.dto.IndexResponse indexResponse =
                agentClient.indexRepository(project.getId(), project.getLocalPath());

            log.info("索引完成: projectId={}, status={}, totalFiles={}, indexedFiles={}",
                project.getId(), indexResponse.getStatus(),
                indexResponse.getTotalFiles(), indexResponse.getIndexedFiles());

            // 更新项目索引信息
            project.setTotalFiles(indexResponse.getTotalFiles());
            project.setIndexedFiles(indexResponse.getIndexedFiles());
            project.setLastIndexedAt(LocalDateTime.now());

            // 根据索引结果更新状态
            if ("COMPLETED".equals(indexResponse.getStatus())) {
                project.setStatus(Project.Status.READY);
                project.setIndexStatus(Project.IndexStatus.COMPLETED);
            } else if ("FAILED".equals(indexResponse.getStatus())) {
                project.setStatus(Project.Status.ERROR);
                project.setIndexStatus(Project.IndexStatus.FAILED);
            }

            projectMapper.updateById(project);

        } catch (Exception e) {
            log.error("索引失败: {}", e.getMessage(), e);
            // 索引失败,更新状态
            project.setStatus(Project.Status.ERROR);
            project.setIndexStatus(Project.IndexStatus.FAILED);
            projectMapper.updateById(project);

            throw new BusinessException("触发索引失败: " + e.getMessage());
        }
    }

    /**
     * 获取项目详情
     *
     * @param userId 用户ID
     * @param projectId 项目ID
     * @return 项目响应
     */
    public ProjectResponse getProject(Long userId, Long projectId) {
        Project project = getProjectEntity(userId, projectId);
        return ProjectResponse.fromEntity(project);
    }

    /**
     * 获取用户的项目列表
     *
     * @param userId 用户ID
     * @return 项目响应列表
     */
    public List<ProjectResponse> getUserProjects(Long userId) {
        log.info("Fetching projects for user: {}", userId);
        List<Project> projects = projectMapper.findByUserId(userId);
        return projects.stream()
                .map(ProjectResponse::fromEntity)
                .collect(Collectors.toList());
    }

    /**
     * 获取用户的项目列表（分页）
     *
     * @param userId 用户ID
     * @param page 页码
     * @param size 每页大小
     * @return 分页项目响应
     */
    public Page<ProjectResponse> getUserProjectsPaged(Long userId, int page, int size) {
        log.info("Fetching paged projects for user: {}, page: {}, size: {}", userId, page, size);

        Page<Project> projectPage = new Page<>(page, size);
        LambdaQueryWrapper<Project> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(Project::getUserId, userId)
                .orderByDesc(Project::getCreatedAt);

        Page<Project> resultPage = projectMapper.selectPage(projectPage, queryWrapper);

        Page<ProjectResponse> responsePage = new Page<>(resultPage.getCurrent(), resultPage.getSize(), resultPage.getTotal());
        responsePage.setRecords(resultPage.getRecords().stream()
                .map(ProjectResponse::fromEntity)
                .collect(Collectors.toList()));

        return responsePage;
    }

    /**
     * 更新项目
     *
     * @param userId 用户ID
     * @param projectId 项目ID
     * @param request 更新请求
     * @return 项目响应
     */
    @Transactional
    public ProjectResponse updateProject(Long userId, Long projectId, UpdateProjectRequest request) {
        log.info("Updating project: {} for user: {}", projectId, userId);

        Project project = getProjectEntity(userId, projectId);

        // 如果更新名称，检查是否重复
        if (StringUtils.hasText(request.getName()) && !request.getName().equals(project.getName())) {
            Project existingProject = projectMapper.findByUserIdAndName(userId, request.getName());
            if (existingProject != null) {
                throw new BusinessException(ResultCode.PROJECT_NAME_EXISTS);
            }
            project.setName(request.getName());
        }

        // 更新其他字段
        if (request.getDescription() != null) {
            project.setDescription(request.getDescription());
        }
        if (request.getRepositoryUrl() != null) {
            project.setRepositoryUrl(request.getRepositoryUrl());
        }
        if (StringUtils.hasText(request.getRepositoryType())) {
            project.setRepositoryType(request.getRepositoryType());
        }

        project.setUpdatedAt(LocalDateTime.now());
        projectMapper.updateById(project);

        log.info("Project updated successfully: {}", projectId);
        return ProjectResponse.fromEntity(project);
    }

    /**
     * 删除项目
     *
     * @param userId 用户ID
     * @param projectId 项目ID
     */
    @Transactional
    public void deleteProject(Long userId, Long projectId) {
        log.info("Deleting project: {} for user: {}", projectId, userId);

        Project project = getProjectEntity(userId, projectId);
        projectMapper.deleteById(project.getId());

        log.info("Project deleted successfully: {}", projectId);
    }

    /**
     * 统计用户的项目数量
     *
     * @param userId 用户ID
     * @return 项目数量
     */
    public long countUserProjects(Long userId) {
        return projectMapper.countByUserId(userId);
    }

    /**
     * 更新项目状态
     *
     * @param projectId 项目ID
     * @param status 新状态
     */
    @Transactional
    public void updateProjectStatus(Long projectId, String status) {
        projectMapper.updateStatus(projectId, status);
    }

    /**
     * 更新索引状态
     *
     * @param projectId 项目ID
     * @param indexStatus 索引状态
     */
    @Transactional
    public void updateIndexStatus(Long projectId, String indexStatus) {
        projectMapper.updateIndexStatus(projectId, indexStatus);
    }

    /**
     * 获取项目实体（内部方法）
     *
     * @param userId 用户ID
     * @param projectId 项目ID
     * @return 项目实体
     */
    private Project getProjectEntity(Long userId, Long projectId) {
        Project project = projectMapper.selectById(projectId);
        if (project == null) {
            throw new BusinessException(ResultCode.PROJECT_NOT_FOUND);
        }

        // 验证项目所属权
        if (!project.getUserId().equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN);
        }

        return project;
    }

    /**
     * 确定仓库类型
     */
    private String determineRepositoryType(CreateProjectRequest request) {
        if (StringUtils.hasText(request.getRepositoryType())) {
            return request.getRepositoryType();
        }

        // 根据URL自动判断仓库类型
        String url = request.getRepositoryUrl();
        if (!StringUtils.hasText(url)) {
            return Project.RepositoryType.LOCAL;
        }

        if (url.contains("github.com")) {
            return Project.RepositoryType.GITHUB;
        } else if (url.contains("gitlab.com") || url.contains("gitlab")) {
            return Project.RepositoryType.GITLAB;
        } else if (url.contains("bitbucket.org")) {
            return Project.RepositoryType.BITBUCKET;
        }

        return Project.RepositoryType.LOCAL;
    }

    /**
     * 触发代码审查
     *
     * @param userId 用户ID
     * @param projectId 项目ID
     * @param level 审查级别 (quick/standard/full)
     * @return 审查任务响应
     */
    public com.codeassistant.user.client.dto.ReviewResponse reviewCode(
        Long userId,
        Long projectId,
        String level
    ) {
        log.info("开始代码审查: userId={}, projectId={}, level={}", userId, projectId, level);

        // 1. 验证项目状态
        Project project = getProjectEntity(userId, projectId);
        if (!Project.IndexStatus.COMPLETED.equals(project.getIndexStatus())) {
            throw new BusinessException(ResultCode.PROJECT_NOT_INDEXED);
        }

        // 2. 构建审查请求
        com.codeassistant.user.client.dto.ReviewRequest request =
            com.codeassistant.user.client.dto.ReviewRequest.builder()
                .projectId(projectId)
                .projectPath(project.getLocalPath())  // 需要项目本地路径
                .level(level != null ? level : "standard")
                .build();

        // 3. 调用Agent服务
        var response = agentClient.reviewCode(request);

        // 4. 创建AsyncTask记录，用于进度轮询和推送
        AsyncTask task = new AsyncTask();
        task.setTaskType(AsyncTask.TaskType.REVIEW);
        task.setStatus(AsyncTask.TaskStatus.PENDING);
        task.setProjectId(projectId);
        // userId 暂不记录到 AsyncTask
        task.setCeleryTaskId(response.getTaskId());
        task.setProgress(0);
        task.setEstimatedTime(response.getEstimatedTime());
        task.setMessage("审查任务已创建");
        task.setCreatedAt(LocalDateTime.now());
        task.setUpdatedAt(LocalDateTime.now());
        asyncTaskMapper.insert(task);

        log.info("创建AsyncTask记录: id={}, celeryTaskId={}", task.getId(), response.getTaskId());

        com.codeassistant.user.client.dto.ReviewResponse frontendResponse =
            com.codeassistant.user.client.dto.ReviewResponse.builder()
                .taskId(String.valueOf(task.getId()))
                .status(response.getStatus())
                .estimatedTime(response.getEstimatedTime())
                .message(response.getMessage())
                .build();

        return frontendResponse;
    }

    /**
     * 查询审查结果
     *
     * @param userId 用户ID
     * @param projectId 项目ID
     * @param taskId 任务ID
     * @return 审查报告
     */
    public Object getReviewResult(Long userId, Long projectId, String taskId) {
        log.info("查询审查结果: userId={}, projectId={}, taskId={}", userId, projectId, taskId);

        // 验证项目所属
        getProjectEntity(userId, projectId);

        // 调用Agent服务
        return agentClient.getReviewResult(taskId);
    }

    /**
     * 处理索引回调
     * Agent 服务索引完成后调用,更新项目状态
     *
     * @param request 回调请求
     */
    @Transactional
    public void handleIndexCallback(com.codeassistant.user.dto.IndexCallbackRequest request) {
        log.info("处理索引回调: projectId={}, status={}", request.getProjectId(), request.getStatus());

        Project project = projectMapper.selectById(request.getProjectId());
        if (project == null) {
            log.error("项目不存在: {}", request.getProjectId());
            throw new BusinessException(ResultCode.PROJECT_NOT_FOUND);
        }

        // 更新索引状态
        project.setIndexStatus(request.getStatus());

        // 根据状态更新项目状态
        if (Project.IndexStatus.COMPLETED.equals(request.getStatus())) {
            project.setStatus(Project.Status.READY);
            project.setTotalFiles(request.getTotalFiles());
            project.setIndexedFiles(request.getIndexedFiles());
            project.setLanguage(request.getLanguage());
            project.setLastIndexedAt(LocalDateTime.now());

            log.info("项目索引完成: projectId={}, totalFiles={}, language={}",
                request.getProjectId(), request.getTotalFiles(), request.getLanguage());

        } else if (Project.IndexStatus.FAILED.equals(request.getStatus())) {
            project.setStatus(Project.Status.ERROR);

            log.error("项目索引失败: projectId={}, error={}",
                request.getProjectId(), request.getErrorMessage());
        }

        project.setUpdatedAt(LocalDateTime.now());
        projectMapper.updateById(project);

        log.info("项目状态已更新: projectId={}, status={}, indexStatus={}",
            project.getId(), project.getStatus(), project.getIndexStatus());
    }
}
