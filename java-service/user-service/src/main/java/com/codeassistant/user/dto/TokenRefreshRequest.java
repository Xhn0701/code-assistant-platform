package com.codeassistant.user.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;

/**
 * Token刷新请求DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
public class TokenRefreshRequest {

    /**
     * 刷新Token
     */
    @NotBlank(message = "刷新Token不能为空")
    private String refreshToken;
}
