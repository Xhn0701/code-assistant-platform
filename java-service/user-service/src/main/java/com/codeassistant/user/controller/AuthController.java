package com.codeassistant.user.controller;

import com.codeassistant.user.common.Result;
import com.codeassistant.user.dto.*;
import com.codeassistant.user.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;

/**
 * 认证控制器
 * 提供用户注册、登录、Token刷新等认证接口
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/auth")
@RequiredArgsConstructor
@Validated
@Tag(name = "认证管理", description = "用户注册、登录、Token管理相关接口")
public class AuthController {

    private final AuthService authService;

    /**
     * 用户注册
     *
     * @param request 注册请求
     * @return 注册成功的用户信息
     */
    @PostMapping("/register")
    @Operation(summary = "用户注册", description = "创建新用户账号，注册成功后默认为未激活状态")
    public Result<UserResponse> register(@Valid @RequestBody RegisterRequest request) {
        log.info("用户注册请求: username={}, email={}", request.getUsername(), request.getEmail());
        UserResponse user = authService.register(request);
        return Result.success(user, "注册成功");
    }

    /**
     * 用户登录
     *
     * @param request 登录请求
     * @return 登录响应（包含JWT Token）
     */
    @PostMapping("/login")
    @Operation(summary = "用户登录", description = "使用用户名或邮箱登录，返回JWT Token")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        log.info("用户登录请求: credential={}", request.getCredential());
        LoginResponse response = authService.login(request);
        return Result.success(response, "登录成功");
    }

    /**
     * 刷新Token
     *
     * @param request 刷新请求
     * @return 新的Token
     */
    @PostMapping("/refresh-token")
    @Operation(summary = "刷新Token", description = "使用刷新Token获取新的访问Token")
    public Result<TokenRefreshResponse> refreshToken(@Valid @RequestBody TokenRefreshRequest request) {
        log.info("Token刷新请求");
        TokenRefreshResponse response = authService.refreshToken(request);
        return Result.success(response, "Token刷新成功");
    }

    /**
     * 用户登出
     * 注意：JWT是无状态的，登出只需要客户端删除Token即可
     * 这个接口主要用于记录登出日志或清理服务端缓存
     *
     * @return 登出结果
     */
    @PostMapping("/logout")
    @Operation(summary = "用户登出", description = "退出登录（客户端删除Token）")
    @SecurityRequirement(name = "Bearer Authentication")
    public Result<Void> logout() {
        log.info("用户登出请求");
        // JWT是无状态的，不需要服务端处理
        // 如果使用了Redis缓存Token，可以在这里清理
        // TODO: Phase 3实现Token黑名单功能
        return Result.success(null, "登出成功");
    }

    /**
     * 测试接口：验证Token是否有效
     * 这是一个受保护的接口，需要认证才能访问
     *
     * @return 当前用户信息
     */
    @GetMapping("/verify")
    @Operation(summary = "验证Token", description = "测试Token是否有效，返回当前用户信息")
    @SecurityRequirement(name = "Bearer Authentication")
    public Result<String> verifyToken() {
        // 如果能访问到这个接口，说明Token有效
        // SecurityUtils.getCurrentUser() 可以获取当前用户信息
        log.info("Token验证请求");
        return Result.success("Token有效", "Token验证成功");
    }
}
