package com.codeassistant.user.security;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Collections;

/**
 * JWT认证过滤器
 * 拦截每个请求，验证JWT Token并设置认证信息
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        try {
            // 1. 从请求头中提取JWT Token
            String token = extractTokenFromRequest(request);

            // 2. 验证Token
            if (StringUtils.hasText(token) && jwtTokenProvider.validateToken(token)) {
                // 3. 检查Token类型（只接受access token）
                String tokenType = jwtTokenProvider.getTokenType(token);
                if (!"access".equals(tokenType)) {
                    log.warn("Invalid token type: {}, expected: access", tokenType);
                    filterChain.doFilter(request, response);
                    return;
                }

                // 4. 从Token中提取用户信息
                Long userId = jwtTokenProvider.getUserIdFromToken(token);
                String username = jwtTokenProvider.getUsernameFromToken(token);
                String role = jwtTokenProvider.getRoleFromToken(token);

                // 5. 创建认证对象
                // 使用ROLE_前缀是Spring Security的约定
                SimpleGrantedAuthority authority = new SimpleGrantedAuthority("ROLE_" + role);
                UsernamePasswordAuthenticationToken authentication =
                        new UsernamePasswordAuthenticationToken(
                                new UserPrincipal(userId, username, role),
                                null,
                                Collections.singletonList(authority)
                        );

                // 6. 设置请求详情
                authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));

                // 7. 将认证信息设置到Security上下文
                SecurityContextHolder.getContext().setAuthentication(authentication);

                log.debug("JWT authentication successful for user: {} (ID: {})", username, userId);
            }
        } catch (Exception e) {
            log.error("Failed to set user authentication in security context: {}", e.getMessage());
            // 不中断请求链，让请求继续，但没有认证信息
        }

        // 继续过滤器链
        filterChain.doFilter(request, response);
    }

    /**
     * 从HTTP请求中提取JWT Token
     *
     * @param request HTTP请求
     * @return Token字符串，不存在返回null
     */
    private String extractTokenFromRequest(HttpServletRequest request) {
        // 从Authorization头提取
        String bearerToken = request.getHeader("Authorization");
        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }

        // 备选方案：从查询参数提取（用于WebSocket等场景）
        String tokenParam = request.getParameter("token");
        if (StringUtils.hasText(tokenParam)) {
            return tokenParam;
        }

        return null;
    }

    /**
     * 用户主体信息
     * 存储在Spring Security的Authentication中
     */
    public static class UserPrincipal {
        private final Long userId;
        private final String username;
        private final String role;

        public UserPrincipal(Long userId, String username, String role) {
            this.userId = userId;
            this.username = username;
            this.role = role;
        }

        public Long getUserId() {
            return userId;
        }

        public String getUsername() {
            return username;
        }

        public String getRole() {
            return role;
        }

        @Override
        public String toString() {
            return username;
        }
    }
}
