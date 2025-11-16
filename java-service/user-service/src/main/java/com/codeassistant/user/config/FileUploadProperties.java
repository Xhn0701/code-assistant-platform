package com.codeassistant.user.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

/**
 * 文件上传配置属性
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Component
@ConfigurationProperties(prefix = "file.upload")
public class FileUploadProperties {

    /**
     * 文件上传目录
     */
    private String path = "uploads/avatars";

    /**
     * 允许的文件类型（逗号分隔）
     */
    private String allowedTypes = "jpg,jpeg,png,gif";

    /**
     * 单个文件最大大小（字节）
     */
    private Long maxSize = 2097152L;  // 2MB

    /**
     * 访问URL前缀
     */
    private String urlPrefix = "/uploads/avatars";

    /**
     * 获取允许的文件类型列表
     *
     * @return 文件类型列表
     */
    public List<String> getAllowedTypesList() {
        return Arrays.asList(allowedTypes.toLowerCase().split(","));
    }
}
