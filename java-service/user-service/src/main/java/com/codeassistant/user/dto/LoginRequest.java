package com.codeassistant.user.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

/**
 * 用户登录请求DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
public class LoginRequest {

    /**
     * 登录凭证：用户名或邮箱
     */
    @NotBlank(message = "登录凭证不能为空")
    private String credential;

    /**
     * 密码
     */
    @NotBlank(message = "密码不能为空")
    private String password;

    /**
     * 是否记住我（生成更长有效期的Token）
     */
    private Boolean rememberMe = false;
}
