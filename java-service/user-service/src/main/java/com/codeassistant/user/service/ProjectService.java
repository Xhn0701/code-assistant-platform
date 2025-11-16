package com.codeassistant.user.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.codeassistant.user.common.BusinessException;
import com.codeassistant.user.common.ResultCode;
import com.codeassistant.user.dto.CreateProjectRequest;
import com.codeassistant.user.dto.ProjectResponse;
import com.codeassistant.user.dto.UpdateProjectRequest;
import com.codeassistant.user.entity.Project;
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

    /**
     * 创建项目
     *
     * @param userId 用户ID
     * @param request 创建请求
     * @return 项目响应
     */
    @Transactional
    public ProjectResponse createProject(Long userId, CreateProjectRequest request) {
        log.info("Creating project for user: {}, name: {}", userId, request.getName());

        // 检查项目名称是否已存在
        Project existingProject = projectMapper.findByUserIdAndName(userId, request.getName());
        if (existingProject != null) {
            throw new BusinessException(ResultCode.PROJECT_NAME_EXISTS);
        }

        // 构建项目实体
        Project project = Project.builder()
                .userId(userId)
                .name(request.getName())
                .description(request.getDescription())
                .repositoryUrl(request.getRepositoryUrl())
                .repositoryType(determineRepositoryType(request))
                .status(Project.Status.CREATED)
                .indexStatus(Project.IndexStatus.PENDING)
                .totalFiles(0)
                .indexedFiles(0)
                .deleted(0)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        // 保存项目
        projectMapper.insert(project);
        log.info("Project created successfully with ID: {}", project.getId());

        return ProjectResponse.fromEntity(project);
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
}
