package com.codeassistant.user.dto;

import lombok.Builder;
import lombok.Data;

/**
 * Token刷新响应DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Builder
public class TokenRefreshResponse {

    /**
     * 新的访问Token
     */
    private String accessToken;

    /**
     * 新的刷新Token
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
}
