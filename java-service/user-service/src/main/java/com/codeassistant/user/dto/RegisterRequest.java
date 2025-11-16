package com.codeassistant.user.dto;

import lombok.Data;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;

/**
 * 用户注册请求DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
public class RegisterRequest {

    /**
     * 用户名：3-20个字符，只能包含字母、数字、下划线
     */
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度必须在3-20个字符之间")
    @Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "用户名只能包含字母、数字、下划线")
    private String username;

    /**
     * 邮箱：必须是有效的邮箱格式
     */
    @NotBlank(message = "邮箱不能为空")
    @Email(message = "邮箱格式不正确")
    @Size(max = 100, message = "邮箱长度不能超过100个字符")
    private String email;

    /**
     * 密码：8-20个字符，必须包含数字和字母
     */
    @NotBlank(message = "密码不能为空")
    @Size(min = 8, max = 20, message = "密码长度必须在8-20个字符之间")
    @Pattern(
        regexp = "^(?=.*[0-9])(?=.*[a-zA-Z]).{8,20}$",
        message = "密码必须包含数字和字母"
    )
    private String password;

    /**
     * 昵称：可选，1-50个字符
     */
    @Size(max = 50, message = "昵称长度不能超过50个字符")
    private String nickname;
}
