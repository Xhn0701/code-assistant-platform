package com.codeassistant.user.service;

import com.codeassistant.user.common.BusinessException;
import com.codeassistant.user.common.ResultCode;
import com.codeassistant.user.dto.UpdatePasswordRequest;
import com.codeassistant.user.dto.UpdateUserRequest;
import com.codeassistant.user.dto.UserResponse;
import com.codeassistant.user.entity.User;
import com.codeassistant.user.mapper.UserMapper;
import com.codeassistant.user.security.SecurityUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 用户服务
 * 处理用户信息查询、更新、密码修改等业务
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;
    private final PasswordEncoder passwordEncoder;

    /**
     * 根据ID获取用户信息
     *
     * @param userId 用户ID
     * @return 用户信息
     */
    public UserResponse getUserById(Long userId) {
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        log.debug("获取用户信息: userId={}, username={}", userId, user.getUsername());
        return convertToUserResponse(user);
    }

    /**
     * 更新用户资料
     * 用户只能更新自己的资料（权限检查）
     *
     * @param userId 用户ID
     * @param request 更新请求
     * @return 更新后的用户信息
     */
    @Transactional(rollbackFor = Exception.class)
    public UserResponse updateUser(Long userId, UpdateUserRequest request) {
        // 1. 权限检查：只能更新自己的资料
        Long currentUserId = SecurityUtils.getCurrentUserId();
        if (!currentUserId.equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权修改其他用户的资料");
        }

        // 2. 查询用户
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        // 3. 更新昵称
        boolean updated = false;
        if (request.getNickname() != null && !request.getNickname().equals(user.getNickname())) {
            user.setNickname(request.getNickname());
            updated = true;
        }

        // 4. 更新邮箱（如果提供）
        if (request.getEmail() != null && !request.getEmail().equals(user.getEmail())) {
            // 检查新邮箱是否已被占用
            User existingUser = userMapper.findByEmailIncludeDeleted(request.getEmail());
            if (existingUser != null && !existingUser.getId().equals(userId)) {
                throw new BusinessException(ResultCode.EMAIL_ALREADY_EXISTS);
            }

            user.setEmail(request.getEmail());
            user.setEmailVerified(false);  // 邮箱变更后需要重新验证
            // TODO: 发送新邮箱验证邮件
            updated = true;
        }

        // 5. 保存更新
        if (updated) {
            int result = userMapper.updateById(user);
            if (result <= 0) {
                throw new BusinessException(ResultCode.INTERNAL_ERROR, "更新用户资料失败");
            }
            log.info("用户资料更新成功: userId={}, username={}", userId, user.getUsername());
        } else {
            log.debug("用户资料无变更: userId={}", userId);
        }

        return convertToUserResponse(user);
    }

    /**
     * 修改密码
     * 用户只能修改自己的密码（权限检查）
     *
     * @param userId 用户ID
     * @param request 修改密码请求
     */
    @Transactional(rollbackFor = Exception.class)
    public void updatePassword(Long userId, UpdatePasswordRequest request) {
        // 1. 权限检查：只能修改自己的密码
        Long currentUserId = SecurityUtils.getCurrentUserId();
        if (!currentUserId.equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权修改其他用户的密码");
        }

        // 2. 验证新密码和确认密码是否一致
        if (!request.getNewPassword().equals(request.getConfirmPassword())) {
            throw new BusinessException(ResultCode.PARAM_ERROR, "新密码与确认密码不一致");
        }

        // 3. 验证新密码不能与当前密码相同
        if (request.getCurrentPassword().equals(request.getNewPassword())) {
            throw new BusinessException(ResultCode.PARAM_ERROR, "新密码不能与当前密码相同");
        }

        // 4. 查询用户
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        // 5. 验证当前密码
        if (!passwordEncoder.matches(request.getCurrentPassword(), user.getPassword())) {
            throw new BusinessException(ResultCode.INVALID_PASSWORD, "当前密码不正确");
        }

        // 6. 更新密码
        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
        int result = userMapper.updateById(user);
        if (result <= 0) {
            throw new BusinessException(ResultCode.INTERNAL_ERROR, "密码修改失败");
        }

        log.info("用户密码修改成功: userId={}, username={}", userId, user.getUsername());

        // TODO: 发送密码修改通知邮件
    }

    /**
     * 更新用户头像URL
     * 由头像上传接口调用
     *
     * @param userId 用户ID
     * @param avatarUrl 头像URL
     * @return 更新后的用户信息
     */
    @Transactional(rollbackFor = Exception.class)
    public UserResponse updateAvatar(Long userId, String avatarUrl) {
        // 1. 权限检查：只能更新自己的头像
        Long currentUserId = SecurityUtils.getCurrentUserId();
        if (!currentUserId.equals(userId)) {
            throw new BusinessException(ResultCode.FORBIDDEN, "无权修改其他用户的头像");
        }

        // 2. 查询用户
        User user = userMapper.selectById(userId);
        if (user == null) {
            throw new BusinessException(ResultCode.USER_NOT_FOUND);
        }

        // 3. 更新头像URL
        String oldAvatarUrl = user.getAvatarUrl();
        user.setAvatarUrl(avatarUrl);
        int result = userMapper.updateById(user);
        if (result <= 0) {
            throw new BusinessException(ResultCode.INTERNAL_ERROR, "头像更新失败");
        }

        log.info("用户头像更新成功: userId={}, oldAvatar={}, newAvatar={}",
                userId, oldAvatarUrl, avatarUrl);

        // TODO: 删除旧头像文件（如果存在）

        return convertToUserResponse(user);
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
}
