package com.codeassistant.user.controller;

import com.codeassistant.user.common.Result;
import com.codeassistant.user.dto.UpdatePasswordRequest;
import com.codeassistant.user.dto.UpdateUserRequest;
import com.codeassistant.user.dto.UserResponse;
import com.codeassistant.user.service.FileStorageService;
import com.codeassistant.user.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import javax.validation.Valid;
import javax.validation.constraints.NotNull;

/**
 * 用户控制器
 * 提供用户信息查询、更新、密码修改、头像上传等接口
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
@Validated
@Tag(name = "用户管理", description = "用户信息查询、更新、密码修改、头像上传相关接口")
@SecurityRequirement(name = "bearerAuth")
public class UserController {

    private final UserService userService;
    private final FileStorageService fileStorageService;

    /**
     * 获取用户信息
     *
     * @param id 用户ID
     * @return 用户信息
     */
    @GetMapping("/{id}")
    @Operation(summary = "获取用户信息", description = "根据用户ID查询用户详细信息")
    public Result<UserResponse> getUserById(
            @Parameter(description = "用户ID", required = true, example = "1")
            @PathVariable("id") @NotNull Long id) {
        log.info("获取用户信息请求: userId={}", id);
        UserResponse user = userService.getUserById(id);
        return Result.success(user);
    }

    /**
     * 更新用户资料
     * 用户只能更新自己的资料
     *
     * @param id 用户ID
     * @param request 更新请求
     * @return 更新后的用户信息
     */
    @PutMapping("/{id}")
    @Operation(summary = "更新用户资料", description = "更新用户昵称、邮箱等信息（仅限本人）")
    public Result<UserResponse> updateUser(
            @Parameter(description = "用户ID", required = true, example = "1")
            @PathVariable("id") @NotNull Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        log.info("更新用户资料请求: userId={}, nickname={}, email={}",
                id, request.getNickname(), request.getEmail());
        UserResponse user = userService.updateUser(id, request);
        return Result.success(user, "用户资料更新成功");
    }

    /**
     * 修改密码
     * 用户只能修改自己的密码
     *
     * @param id 用户ID
     * @param request 修改密码请求
     * @return 操作结果
     */
    @PutMapping("/{id}/password")
    @Operation(summary = "修改密码", description = "修改用户密码（需要验证当前密码，仅限本人）")
    public Result<Void> updatePassword(
            @Parameter(description = "用户ID", required = true, example = "1")
            @PathVariable("id") @NotNull Long id,
            @Valid @RequestBody UpdatePasswordRequest request) {
        log.info("修改密码请求: userId={}", id);
        userService.updatePassword(id, request);
        return Result.success(null, "密码修改成功");
    }

    /**
     * 上传头像
     * 用户只能上传自己的头像
     *
     * @param id 用户ID
     * @param file 头像文件
     * @return 更新后的用户信息（包含新头像URL）
     */
    @PostMapping("/{id}/avatar")
    @Operation(summary = "上传头像", description = "上传用户头像图片（仅限本人，支持JPG/PNG/GIF，最大2MB）")
    public Result<UserResponse> uploadAvatar(
            @Parameter(description = "用户ID", required = true, example = "1")
            @PathVariable("id") @NotNull Long id,
            @Parameter(description = "头像文件（JPG/PNG/GIF，最大2MB）", required = true)
            @RequestParam("file") @NotNull MultipartFile file) {
        log.info("上传头像请求: userId={}, fileName={}, fileSize={}",
                id, file.getOriginalFilename(), file.getSize());

        // 1. 保存文件到本地存储
        String avatarUrl = fileStorageService.storeFile(file);

        // 2. 更新用户头像URL
        UserResponse user = userService.updateAvatar(id, avatarUrl);

        return Result.success(user, "头像上传成功");
    }
}
