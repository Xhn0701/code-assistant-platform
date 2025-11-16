package com.codeassistant.user.common;

import lombok.Getter;

/**
 * 返回码枚举
 */
@Getter
public enum ResultCode {

    // ========== 通用状态码 ==========
    SUCCESS(200, "操作成功"),
    FAIL(400, "操作失败"),
    UNAUTHORIZED(401, "未授权，请先登录"),
    FORBIDDEN(403, "没有权限访问"),
    NOT_FOUND(404, "资源不存在"),
    INTERNAL_ERROR(500, "服务器内部错误"),

    // ========== 参数校验 (1000-1099) ==========
    PARAM_ERROR(1000, "参数错误"),
    PARAM_MISSING(1001, "缺少必填参数"),
    PARAM_TYPE_ERROR(1002, "参数类型错误"),
    PARAM_VALIDATE_ERROR(1003, "参数校验失败"),

    // ========== 用户相关 (2000-2099) ==========
    USER_NOT_FOUND(2000, "用户不存在"),
    USER_ALREADY_EXISTS(2001, "用户已存在"),
    USERNAME_ALREADY_EXISTS(2002, "用户名已存在"),
    EMAIL_ALREADY_EXISTS(2003, "邮箱已被注册"),
    INVALID_PASSWORD(2004, "密码错误"),
    USER_BANNED(2005, "用户已被封禁"),
    USER_NOT_ACTIVATED(2006, "用户未激活"),

    // ========== Token相关 (2100-2199) ==========
    TOKEN_MISSING(2100, "Token缺失"),
    TOKEN_INVALID(2101, "Token无效"),
    TOKEN_EXPIRED(2102, "Token已过期"),
    INVALID_TOKEN(2103, "非法的Token"),

    // ========== 项目相关 (3000-3099) ==========
    PROJECT_NOT_FOUND(3000, "项目不存在"),
    PROJECT_ALREADY_EXISTS(3001, "项目已存在"),
    PROJECT_ACCESS_DENIED(3002, "无权访问该项目"),
    PROJECT_NAME_EXISTS(3003, "项目名称已存在"),

    // ========== 外部服务 (4000-4099) ==========
    AGENT_SERVICE_ERROR(4000, "Agent服务调用失败"),
    GITHUB_API_ERROR(4001, "GitHub API调用失败"),

    // ========== 业务逻辑 (5000-5099) ==========
    BUSINESS_ERROR(5000, "业务处理失败"),
    ;

    /**
     * 状态码
     */
    private final Integer code;

    /**
     * 提示信息
     */
    private final String message;

    ResultCode(Integer code, String message) {
        this.code = code;
        this.message = message;
    }
}
