package com.codeassistant.user.dto;

import lombok.Builder;
import lombok.Data;

/**
 * 用户登录响应DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Builder
public class LoginResponse {

    /**
     * 访问Token（用于API请求认证）
     */
    private String accessToken;

    /**
     * 刷新Token（用于获取新的访问Token）
     */
    private String refreshToken;

    /**
     * Token类型（固定为 Bearer）
     */
    @Builder.Default
    private String tokenType = "Bearer";

    /**
     * 访问Token过期时间（秒）
     */
    private Long expiresIn;

    /**
     * 用户信息
     */
    private UserResponse user;
}
