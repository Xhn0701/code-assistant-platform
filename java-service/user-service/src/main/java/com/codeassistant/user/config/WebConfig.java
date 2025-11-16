package com.codeassistant.user.config;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Paths;

/**
 * Web配置
 * 配置静态资源访问路径
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Configuration
@RequiredArgsConstructor
public class WebConfig implements WebMvcConfigurer {

    private final FileUploadProperties fileUploadProperties;

    /**
     * 配置静态资源处理
     * 将上传的文件映射到HTTP可访问的路径
     */
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 获取上传目录的绝对路径
        String uploadPath = Paths.get(fileUploadProperties.getPath())
                .toAbsolutePath()
                .normalize()
                .toString();

        // 映射 /uploads/avatars/** 到实际的文件系统路径
        registry.addResourceHandler(fileUploadProperties.getUrlPrefix() + "/**")
                .addResourceLocations("file:" + uploadPath + "/");
    }
}
