package com.codeassistant.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 项目实体类
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("projects")
public class Project {

    /**
     * 项目ID - 主键自增
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 所属用户ID
     */
    @TableField("user_id")
    private Long userId;

    /**
     * 项目名称
     */
    @TableField("name")
    private String name;

    /**
     * 项目描述
     */
    @TableField("description")
    private String description;

    /**
     * 代码仓库URL
     */
    @TableField("repository_url")
    private String repositoryUrl;

    /**
     * 仓库类型
     * GITHUB, GITLAB, BITBUCKET, LOCAL
     */
    @TableField("repository_type")
    private String repositoryType;

    /**
     * 项目状态
     * CREATED: 已创建
     * INDEXING: 索引中
     * READY: 就绪
     * ERROR: 错误
     */
    @TableField("status")
    private String status;

    /**
     * 索引状态
     * PENDING: 待索引
     * INDEXING: 索引中
     * COMPLETED: 已完成
     * FAILED: 失败
     */
    @TableField("index_status")
    private String indexStatus;

    /**
     * 主要编程语言
     */
    @TableField("language")
    private String language;

    /**
     * 总文件数
     */
    @TableField("total_files")
    private Integer totalFiles;

    /**
     * 已索引文件数
     */
    @TableField("indexed_files")
    private Integer indexedFiles;

    /**
     * 最后索引时间
     */
    @TableField("last_indexed_at")
    private LocalDateTime lastIndexedAt;

    /**
     * 逻辑删除标记
     */
    @TableLogic
    @TableField("deleted")
    private Integer deleted;

    /**
     * 创建时间
     */
    @TableField(value = "created_at", fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    @TableField(value = "updated_at", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /**
     * 项目状态枚举
     */
    public static class Status {
        public static final String CREATED = "CREATED";
        public static final String INDEXING = "INDEXING";
        public static final String READY = "READY";
        public static final String ERROR = "ERROR";
    }

    /**
     * 仓库类型枚举
     */
    public static class RepositoryType {
        public static final String GITHUB = "GITHUB";
        public static final String GITLAB = "GITLAB";
        public static final String BITBUCKET = "BITBUCKET";
        public static final String LOCAL = "LOCAL";
    }

    /**
     * 索引状态枚举
     */
    public static class IndexStatus {
        public static final String PENDING = "PENDING";
        public static final String INDEXING = "INDEXING";
        public static final String COMPLETED = "COMPLETED";
        public static final String FAILED = "FAILED";
    }
}
