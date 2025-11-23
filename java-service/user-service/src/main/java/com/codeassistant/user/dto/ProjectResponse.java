package com.codeassistant.user.dto;

import com.codeassistant.user.entity.Project;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 项目响应DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProjectResponse {

    private Long id;
    private Long userId;
    private String name;
    private String description;
    private String repositoryUrl;
    private String repositoryType;
    private String localPath;
    private String status;
    private String indexStatus;
    private String language;
    private Integer totalFiles;
    private Integer indexedFiles;
    private LocalDateTime lastIndexedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    /**
     * 从实体转换为响应DTO
     */
    public static ProjectResponse fromEntity(Project project) {
        if (project == null) {
            return null;
        }
        return ProjectResponse.builder()
                .id(project.getId())
                .userId(project.getUserId())
                .name(project.getName())
                .description(project.getDescription())
                .repositoryUrl(project.getRepositoryUrl())
                .repositoryType(project.getRepositoryType())
                .localPath(project.getLocalPath())
                .status(project.getStatus())
                .indexStatus(project.getIndexStatus())
                .language(project.getLanguage())
                .totalFiles(project.getTotalFiles())
                .indexedFiles(project.getIndexedFiles())
                .lastIndexedAt(project.getLastIndexedAt())
                .createdAt(project.getCreatedAt())
                .updatedAt(project.getUpdatedAt())
                .build();
    }
}
