package com.codeassistant.user.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.Components;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI/Swagger配置
 * SpringDoc OpenAPI 3.x 自动生成API文档
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Configuration
public class OpenApiConfig {

    /**
     * OpenAPI配置
     */
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(apiInfo())
                .components(securityComponents())
                .addSecurityItem(new SecurityRequirement().addList("Bearer Authentication"));
    }

    /**
     * API基本信息
     */
    private Info apiInfo() {
        return new Info()
                .title("User Service API")
                .description("代码助手平台 - 用户管理微服务API文档")
                .version("1.0.0")
                .contact(new Contact()
                        .name("Code Assistant Platform")
                        .email("support@codeassistant.com")
                        .url("https://github.com/your-org/code-assistant-platform"))
                .license(new License()
                        .name("MIT License")
                        .url("https://opensource.org/licenses/MIT"));
    }

    /**
     * 安全配置 - JWT认证
     */
    private Components securityComponents() {
        return new Components()
                .addSecuritySchemes("Bearer Authentication",
                        new SecurityScheme()
                                .type(SecurityScheme.Type.HTTP)
                                .scheme("bearer")
                                .bearerFormat("JWT")
                                .description("请输入JWT Token，格式：Bearer {token}")
                );
    }
}
