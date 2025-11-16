package com.codeassistant.user.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 用户实体类
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("users")
public class User {

    /**
     * 用户ID - 主键自增
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 用户名 - 唯一，3-20个字符
     */
    @TableField("username")
    private String username;

    /**
     * 邮箱 - 唯一，用于登录和通知
     */
    @TableField("email")
    private String email;

    /**
     * 密码 - BCrypt加密存储
     * JsonIgnore: 防止在JSON序列化时泄露密码
     */
    @JsonIgnore
    @TableField("password")
    private String password;

    /**
     * 昵称 - 显示名称
     */
    @TableField("nickname")
    private String nickname;

    /**
     * 头像URL
     */
    @TableField("avatar_url")
    private String avatarUrl;

    /**
     * 用户状态
     * ACTIVE: 正常
     * INACTIVE: 未激活
     * BANNED: 已封禁
     */
    @TableField("status")
    private String status;

    /**
     * 用户角色
     * USER: 普通用户
     * ADMIN: 管理员
     */
    @TableField("role")
    private String role;

    /**
     * 最后登录时间
     */
    @TableField("last_login_at")
    private LocalDateTime lastLoginAt;

    /**
     * 最后登录IP
     */
    @TableField("last_login_ip")
    private String lastLoginIp;

    /**
     * 邮箱验证状态
     */
    @TableField("email_verified")
    private Boolean emailVerified;

    /**
     * 邮箱验证Token
     */
    @JsonIgnore
    @TableField("email_verify_token")
    private String emailVerifyToken;

    /**
     * 逻辑删除标记 (0=未删除, 1=已删除)
     * MyBatis-Plus自动处理逻辑删除
     */
    @TableLogic
    @TableField("deleted")
    private Integer deleted;

    /**
     * 创建时间 - 自动填充
     */
    @TableField(value = "created_at", fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新时间 - 自动填充
     */
    @TableField(value = "updated_at", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /**
     * 用户状态枚举
     */
    public static class Status {
        public static final String ACTIVE = "ACTIVE";
        public static final String INACTIVE = "INACTIVE";
        public static final String BANNED = "BANNED";
    }

    /**
     * 用户角色枚举
     */
    public static class Role {
        public static final String USER = "USER";
        public static final String ADMIN = "ADMIN";
    }
}
