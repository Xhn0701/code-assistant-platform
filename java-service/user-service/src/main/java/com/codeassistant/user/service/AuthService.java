package com.codeassistant.user.service;

import com.codeassistant.user.common.BusinessException;
import com.codeassistant.user.common.ResultCode;
import com.codeassistant.user.dto.*;
import com.codeassistant.user.entity.User;
import com.codeassistant.user.mapper.UserMapper;
import com.codeassistant.user.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.servlet.http.HttpServletRequest;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * 认证服务
 * 处理用户注册、登录、Token刷新等认证相关业务
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final HttpServletRequest request;

    @Value("${jwt.expiration}")
    private Long jwtExpiration;

    /**
     * 用户注册
     *
     * @param registerRequest 注册请求
     * @return 用户信息
     */
    @Transactional(rollbackFor = Exception.class)
    public UserResponse register(RegisterRequest registerRequest) {
        // 1. 检查用户名是否已存在
        User existingUser = userMapper.findByUsernameIncludeDeleted(registerRequest.getUsername());
        if (existingUser != null) {
            throw new BusinessException(ResultCode.USERNAME_ALREADY_EXISTS);
        }

        // 2. 检查邮箱是否已存在
        existingUser = userMapper.findByEmailIncludeDeleted(registerRequest.getEmail());
        if (existingUser != null) {
            throw new BusinessException(ResultCode.EMAIL_ALREADY_EXISTS);
        }

        // 3. 创建用户对象
        User user = User.builder()
                .username(registerRequest.getUsername())
                .email(registerRequest.getEmail())
                .password(passwordEncoder.encode(registerRequest.getPassword()))
                .nickname(registerRequest.getNickname() != null ?
                        registerRequest.getNickname() : registerRequest.getUsername())
                .status(User.Status.INACTIVE)  // 默认未激活，需要验证邮箱
                .role(User.Role.USER)  // 默认角色
                .emailVerified(false)
                .emailVerifyToken(UUID.randomUUID().toString())  // 生成邮箱验证Token
                .deleted(0)
                .build();

        // 4. 保存用户
        int result = userMapper.insert(user);
        if (result <= 0) {
            throw new BusinessException(ResultCode.INTERNAL_ERROR, "用户注册失败");
        }

        log.info("用户注册成功: username={}, email={}, id={}", user.getUsername(), user.getEmail(), user.getId());

        // TODO: 发送邮箱验证邮件（Phase 3实现）
        // emailService.sendVerificationEmail(user.getEmail(), user.getEmailVerifyToken());

        // 5. 返回用户信息
        return convertToUserResponse(user);
    }

    /**
     * 用户登录
     *
     * @param loginRequest 登录请求
     * @return 登录响应（包含Token）
     */
    @Transactional(rollbackFor = Exception.class)
    public LoginResponse login(LoginRequest loginRequest) {
        // 1. 查找用户（支持用户名或邮箱登录）
        User user = findUserByCredential(loginRequest.getCredential());
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        // 2. 验证密码
        if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPassword())) {
            throw new BusinessException(ResultCode.INVALID_PASSWORD);
        }

        // 3. 检查用户状态
        if (User.Status.BANNED.equals(user.getStatus())) {
            throw new BusinessException(ResultCode.USER_BANNED);
        }

        // 注意：未激活的用户也允许登录，但会在响应中标记emailVerified=false
        // 前端可以根据这个字段提示用户验证邮箱

        // 4. 生成Token
        String accessToken = jwtTokenProvider.generateAccessToken(user.getId(), user.getUsername(), user.getRole());
        String refreshToken = jwtTokenProvider.generateRefreshToken(user.getId(), user.getUsername());

        // 5. 更新最后登录信息
        String clientIp = getClientIp();
        userMapper.updateLastLogin(user.getId(), LocalDateTime.now(), clientIp);

        log.info("用户登录成功: username={}, id={}, ip={}", user.getUsername(), user.getId(), clientIp);

        // 6. 构建响应
        return LoginResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .expiresIn(jwtExpiration / 1000)  // 转换为秒
                .user(convertToUserResponse(user))
                .build();
    }

    /**
     * 刷新Token
     *
     * @param refreshRequest 刷新请求
     * @return 新的Token
     */
    public TokenRefreshResponse refreshToken(TokenRefreshRequest refreshRequest) {
        String refreshToken = refreshRequest.getRefreshToken();

        // 1. 验证刷新Token
        if (!jwtTokenProvider.validateToken(refreshToken)) {
            throw new BusinessException(ResultCode.TOKEN_INVALID, "刷新Token无效");
        }

        // 2. 检查Token类型
        String tokenType = jwtTokenProvider.getTokenType(refreshToken);
        if (!"refresh".equals(tokenType)) {
            throw new BusinessException(ResultCode.TOKEN_INVALID, "Token类型错误");
        }

        // 3. 从Token中提取用户信息
        Long userId = jwtTokenProvider.getUserIdFromToken(refreshToken);
        String username = jwtTokenProvider.getUsernameFromToken(refreshToken);

        // 4. 查询用户（确保用户仍然存在且状态正常）
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }
        if (User.Status.BANNED.equals(user.getStatus())) {
            throw new BusinessException(ResultCode.USER_BANNED);
        }

        // 5. 生成新的Token
        String newAccessToken = jwtTokenProvider.generateAccessToken(user.getId(), user.getUsername(), user.getRole());
        String newRefreshToken = jwtTokenProvider.generateRefreshToken(user.getId(), user.getUsername());

        log.info("Token刷新成功: username={}, id={}", username, userId);

        // 6. 返回新Token
        return TokenRefreshResponse.builder()
                .accessToken(newAccessToken)
                .refreshToken(newRefreshToken)
                .tokenType("Bearer")
                .expiresIn(jwtExpiration / 1000)
                .build();
    }

    /**
     * 根据凭证查找用户（支持用户名或邮箱）
     *
     * @param credential 用户名或邮箱
     * @return 用户对象
     */
    private User findUserByCredential(String credential) {
        // 判断是邮箱还是用户名
        if (credential.contains("@")) {
            return userMapper.findByEmail(credential);
        } else {
            return userMapper.findByUsername(credential);
        }
    }

    /**
     * 将User实体转换为UserResponse DTO
     *
     * @param user 用户实体
     * @return 用户响应DTO
     */
    private UserResponse convertToUserResponse(User user) {
        return UserResponse.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .nickname(user.getNickname())
                .avatarUrl(user.getAvatarUrl())
                .status(user.getStatus())
                .role(user.getRole())
                .emailVerified(user.getEmailVerified())
                .lastLoginAt(user.getLastLoginAt())
                .createdAt(user.getCreatedAt())
                .build();
    }

    /**
     * 获取客户端IP地址
     *
     * @return IP地址
     */
    private String getClientIp() {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("WL-Proxy-Client-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        // 如果有多个IP，取第一个
        if (ip != null && ip.contains(",")) {
            ip = ip.split(",")[0].trim();
        }
        return ip;
    }
}
