package com.codeassistant.user.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Pattern;
import javax.validation.constraints.Size;

/**
 * 修改密码请求DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Schema(description = "修改密码请求")
public class UpdatePasswordRequest {

    /**
     * 当前密码（用于验证）
     */
    @Schema(description = "当前密码", example = "OldPassword123!")
    @NotBlank(message = "当前密码不能为空")
    private String currentPassword;

    /**
     * 新密码
     */
    @Schema(description = "新密码（8-20个字符，必须包含数字和字母）", example = "NewPassword123!")
    @NotBlank(message = "新密码不能为空")
    @Size(min = 8, max = 20, message = "密码长度必须在8-20个字符之间")
    @Pattern(
        regexp = "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d@$!%*#?&]{8,20}$",
        message = "密码必须包含至少一个字母和一个数字"
    )
    private String newPassword;

    /**
     * 确认新密码
     */
    @Schema(description = "确认新密码", example = "NewPassword123!")
    @NotBlank(message = "确认密码不能为空")
    private String confirmPassword;
}
