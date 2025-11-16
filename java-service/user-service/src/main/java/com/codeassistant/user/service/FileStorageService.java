package com.codeassistant.user.service;

import com.codeassistant.user.common.BusinessException;
import com.codeassistant.user.common.ResultCode;
import com.codeassistant.user.config.FileUploadProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import javax.annotation.PostConstruct;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

/**
 * 文件存储服务
 * 处理文件上传、存储、删除等操作
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FileStorageService {

    private final FileUploadProperties fileUploadProperties;
    private Path uploadPath;

    /**
     * 初始化上传目录
     */
    @PostConstruct
    public void init() {
        try {
            uploadPath = Paths.get(fileUploadProperties.getPath()).toAbsolutePath().normalize();
            Files.createDirectories(uploadPath);
            log.info("文件上传目录初始化成功: {}", uploadPath);
        } catch (IOException e) {
            log.error("无法创建文件上传目录: {}", uploadPath, e);
            throw new RuntimeException("无法创建文件上传目录", e);
        }
    }

    /**
     * 存储文件（头像上传）
     *
     * @param file 上传的文件
     * @return 文件访问URL
     */
    public String storeFile(MultipartFile file) {
        // 1. 验证文件
        validateFile(file);

        // 2. 生成唯一文件名
        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());
        String fileExtension = getFileExtension(originalFilename);
        String fileName = generateUniqueFileName(fileExtension);

        try {
            // 3. 保存文件
            Path targetLocation = uploadPath.resolve(fileName);
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);

            log.info("文件上传成功: originalName={}, savedName={}, size={}",
                    originalFilename, fileName, file.getSize());

            // 4. 返回访问URL
            return fileUploadProperties.getUrlPrefix() + "/" + fileName;
        } catch (IOException e) {
            log.error("文件保存失败: {}", fileName, e);
            throw new BusinessException(ResultCode.INTERNAL_ERROR, "文件保存失败");
        }
    }

    /**
     * 删除文件
     *
     * @param fileUrl 文件URL
     */
    public void deleteFile(String fileUrl) {
        if (fileUrl == null || fileUrl.isEmpty()) {
            return;
        }

        try {
            // 从URL中提取文件名
            String fileName = fileUrl.substring(fileUrl.lastIndexOf("/") + 1);
            Path filePath = uploadPath.resolve(fileName);

            // 删除文件
            Files.deleteIfExists(filePath);
            log.info("文件删除成功: {}", fileName);
        } catch (IOException e) {
            log.error("文件删除失败: {}", fileUrl, e);
            // 删除失败不抛出异常，仅记录日志
        }
    }

    /**
     * 验证文件
     *
     * @param file 上传的文件
     */
    private void validateFile(MultipartFile file) {
        // 1. 检查文件是否为空
        if (file == null || file.isEmpty()) {
            throw new BusinessException(ResultCode.PARAM_ERROR, "文件不能为空");
        }

        // 2. 检查文件名
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null || originalFilename.contains("..")) {
            throw new BusinessException(ResultCode.PARAM_ERROR, "文件名无效");
        }

        // 3. 检查文件大小
        if (file.getSize() > fileUploadProperties.getMaxSize()) {
            throw new BusinessException(ResultCode.PARAM_ERROR,
                    String.format("文件大小超过限制（最大%dMB）",
                            fileUploadProperties.getMaxSize() / 1024 / 1024));
        }

        // 4. 检查文件类型
        String fileExtension = getFileExtension(originalFilename);
        if (!fileUploadProperties.getAllowedTypesList().contains(fileExtension.toLowerCase())) {
            throw new BusinessException(ResultCode.PARAM_ERROR,
                    "不支持的文件类型，仅支持: " + fileUploadProperties.getAllowedTypes());
        }

        log.debug("文件验证通过: name={}, size={}, type={}",
                originalFilename, file.getSize(), fileExtension);
    }

    /**
     * 获取文件扩展名
     *
     * @param filename 文件名
     * @return 扩展名（小写，不含点）
     */
    private String getFileExtension(String filename) {
        if (filename == null || !filename.contains(".")) {
            return "";
        }
        return filename.substring(filename.lastIndexOf(".") + 1).toLowerCase();
    }

    /**
     * 生成唯一文件名
     * 格式: yyyyMMdd_UUID.ext
     *
     * @param extension 文件扩展名
     * @return 唯一文件名
     */
    private String generateUniqueFileName(String extension) {
        String datePrefix = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String uuid = UUID.randomUUID().toString().replace("-", "");
        return String.format("%s_%s.%s", datePrefix, uuid, extension);
    }

    /**
     * 获取文件的绝对路径
     *
     * @param fileName 文件名
     * @return 文件绝对路径
     */
    public Path getFilePath(String fileName) {
        return uploadPath.resolve(fileName).normalize();
    }
}
