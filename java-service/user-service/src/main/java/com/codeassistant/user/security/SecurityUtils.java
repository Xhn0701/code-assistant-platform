package com.codeassistant.user.security;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

/**
 * Security工具类
 * 提供便捷方法获取当前认证用户信息
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
public class SecurityUtils {

    /**
     * 获取当前认证的用户主体
     *
     * @return UserPrincipal对象，未认证返回null
     */
    public static JwtAuthenticationFilter.UserPrincipal getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.getPrincipal() instanceof JwtAuthenticationFilter.UserPrincipal) {
            return (JwtAuthenticationFilter.UserPrincipal) authentication.getPrincipal();
        }
        return null;
    }

    /**
     * 获取当前用户ID
     *
     * @return 用户ID，未认证返回null
     */
    public static Long getCurrentUserId() {
        JwtAuthenticationFilter.UserPrincipal user = getCurrentUser();
        return user != null ? user.getUserId() : null;
    }

    /**
     * 获取当前用户名
     *
     * @return 用户名，未认证返回null
     */
    public static String getCurrentUsername() {
        JwtAuthenticationFilter.UserPrincipal user = getCurrentUser();
        return user != null ? user.getUsername() : null;
    }

    /**
     * 获取当前用户角色
     *
     * @return 角色，未认证返回null
     */
    public static String getCurrentUserRole() {
        JwtAuthenticationFilter.UserPrincipal user = getCurrentUser();
        return user != null ? user.getRole() : null;
    }

    /**
     * 检查是否已认证
     *
     * @return true=已认证, false=未认证
     */
    public static boolean isAuthenticated() {
        return getCurrentUser() != null;
    }

    /**
     * 检查当前用户是否是管理员
     *
     * @return true=是管理员, false=不是
     */
    public static boolean isAdmin() {
        String role = getCurrentUserRole();
        return "ADMIN".equals(role);
    }
}
