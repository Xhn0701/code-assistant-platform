package com.codeassistant.user.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import javax.validation.constraints.Email;
import javax.validation.constraints.Size;

/**
 * 更新用户资料请求DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Schema(description = "更新用户资料请求")
public class UpdateUserRequest {

    /**
     * 昵称
     */
    @Schema(description = "昵称（2-50个字符）", example = "张三")
    @Size(min = 2, max = 50, message = "昵称长度必须在2-50个字符之间")
    private String nickname;

    /**
     * 邮箱（可选，如果提供则需要重新验证）
     */
    @Schema(description = "邮箱地址", example = "newemail@example.com")
    @Email(message = "邮箱格式不正确")
    private String email;
}
