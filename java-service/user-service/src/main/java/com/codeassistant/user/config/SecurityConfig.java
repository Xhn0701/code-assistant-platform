package com.codeassistant.user.config;

import com.codeassistant.user.security.JwtAuthenticationFilter;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * Spring Security配置
 *
 * 实现基于JWT的无状态认证和授权
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity(prePostEnabled = true)  // 启用方法级别的权限控制
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                // 禁用CSRF（前后端分离项目，使用JWT无需CSRF保护）
                .csrf(csrf -> csrf.disable())

                // 禁用CORS（在CorsConfig中单独配置）
                .cors(cors -> {})

                // 会话管理：无状态（不使用Session）
                .sessionManagement(session ->
                    session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                )

                // URL授权配置
                .authorizeHttpRequests(auth -> auth
                        // 公开接口：无需认证
                         .antMatchers(
                                "/api/v1/auth/register",      // 注册
                                "/api/v1/auth/login",         // 登录
                                "/api/v1/auth/refresh-token", // 刷新Token
                                "/api/health/**",             // 健康检查
                                "/actuator/**",               // 监控端点
                                "/swagger-ui/**",             // Swagger UI
                                "/swagger-ui.html",           // Swagger页面
                                "/v3/api-docs/**",            // OpenAPI文档
                                "/api-docs/**",               // SpringDoc API文档
                                "/swagger-resources/**",      // Swagger资源
                                "/webjars/**"                 // Swagger依赖
                        ).permitAll()

                        // OPTIONS请求允许（CORS预检请求）
                        .antMatchers(HttpMethod.OPTIONS, "/**").permitAll()

                        // 管理员接口：需要ADMIN角色
                        .antMatchers("/api/v1/admin/**").hasRole("ADMIN")

                        // 其他所有接口：需要认证
                        .anyRequest().authenticated()
                )

                // 添加JWT过滤器（在UsernamePasswordAuthenticationFilter之前）
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)

                // 异常处理
                .exceptionHandling(exception -> exception
                        // 未认证异常处理
                        .authenticationEntryPoint((request, response, authException) -> {
                            response.setStatus(401);
                            response.setContentType("application/json;charset=UTF-8");
                            response.getWriter().write("{\"code\":401,\"message\":\"未认证，请先登录\"}");
                        })
                        // 权限不足异常处理
                        .accessDeniedHandler((request, response, accessDeniedException) -> {
                            response.setStatus(403);
                            response.setContentType("application/json;charset=UTF-8");
                            response.getWriter().write("{\"code\":403,\"message\":\"权限不足，无法访问\"}");
                        })
                );

        return http.build();
    }

    /**
     * 密码加密器（BCrypt）
     * strength=10: BCrypt加密强度（默认值，平衡安全性和性能）
     */
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(10);
    }
}
