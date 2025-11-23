package com.codeassistant.user.service;

import com.codeassistant.user.common.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * Git 仓库管理服务
 * 负责克隆、更新远程仓库
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Slf4j
@Service
public class GitService {

    @Value("${project.repository.base-path:/tmp/code-assistant}")
    private String baseRepositoryPath;

    @Value("${project.repository.clone-timeout:300}")
    private int cloneTimeoutSeconds;

    /**
     * 克隆 Git 仓库到本地
     *
     * @param repositoryUrl Git 仓库 URL
     * @param projectId 项目 ID (用于生成唯一目录名)
     * @return 本地克隆路径
     */
    public String cloneRepository(String repositoryUrl, Long projectId) {
        if (!StringUtils.hasText(repositoryUrl)) {
            throw new BusinessException("仓库 URL 不能为空");
        }

        // 生成本地存储路径
        String projectDir = generateProjectDirectory(projectId);
        Path localPath = Paths.get(baseRepositoryPath, projectDir);

        try {
            // 确保基础目录存在
            Files.createDirectories(localPath.getParent());

            // 如果目录已存在，先删除
            if (Files.exists(localPath)) {
                log.info("目录已存在,删除旧目录: {}", localPath);
                deleteDirectory(localPath.toFile());
            }

            // 执行 git clone
            log.info("开始克隆仓库: {} -> {}", repositoryUrl, localPath);
            executeGitClone(repositoryUrl, localPath.toString());
            log.info("仓库克隆成功: {}", localPath);

            return localPath.toString();

        } catch (IOException e) {
            log.error("克隆仓库失败: {}", e.getMessage(), e);
            throw new BusinessException("克隆仓库失败: " + e.getMessage());
        }
    }

    /**
     * 更新已存在的仓库
     *
     * @param localPath 本地仓库路径
     * @return 是否更新成功
     */
    public boolean pullRepository(String localPath) {
        if (!StringUtils.hasText(localPath)) {
            return false;
        }

        Path repoPath = Paths.get(localPath);
        if (!Files.exists(repoPath) || !Files.isDirectory(repoPath)) {
            log.warn("仓库路径不存在: {}", localPath);
            return false;
        }

        try {
            log.info("开始拉取最新代码: {}", localPath);
            executeGitPull(localPath);
            log.info("代码拉取成功: {}", localPath);
            return true;

        } catch (Exception e) {
            log.error("拉取代码失败: {}", e.getMessage(), e);
            return false;
        }
    }

    /**
     * 检查本地路径是否有效
     *
     * @param localPath 本地路径
     * @return 是否有效
     */
    public boolean validateLocalPath(String localPath) {
        if (!StringUtils.hasText(localPath)) {
            return false;
        }

        Path path = Paths.get(localPath);
        return Files.exists(path) && Files.isDirectory(path);
    }

    /**
     * 执行 git clone 命令
     */
    private void executeGitClone(String repositoryUrl, String targetPath) {
        List<String> command = new ArrayList<>();
        command.add("git");
        command.add("clone");
        command.add("--depth");
        command.add("1");  // 浅克隆,只克隆最新提交
        command.add(repositoryUrl);
        command.add(targetPath);

        executeCommand(command, null, cloneTimeoutSeconds);
    }

    /**
     * 执行 git pull 命令
     */
    private void executeGitPull(String localPath) {
        List<String> command = new ArrayList<>();
        command.add("git");
        command.add("pull");
        command.add("--rebase");

        executeCommand(command, localPath, 60);  // pull 超时 60 秒
    }

    /**
     * 执行 Shell 命令
     */
    private void executeCommand(List<String> command, String workingDir, int timeoutSeconds) {
        ProcessBuilder processBuilder = new ProcessBuilder(command);

        if (StringUtils.hasText(workingDir)) {
            processBuilder.directory(new File(workingDir));
        }

        processBuilder.redirectErrorStream(true);

        try {
            Process process = processBuilder.start();

            // 读取输出
            StringBuilder output = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                    log.debug("Git 输出: {}", line);
                }
            }

            // 等待命令执行完成
            boolean finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS);

            if (!finished) {
                process.destroyForcibly();
                throw new BusinessException("Git 命令执行超时");
            }

            int exitCode = process.exitValue();
            if (exitCode != 0) {
                log.error("Git 命令执行失败,退出码: {}, 输出: {}", exitCode, output);
                throw new BusinessException("Git 命令执行失败: " + output);
            }

        } catch (IOException e) {
            throw new BusinessException("执行 Git 命令失败: " + e.getMessage());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BusinessException("Git 命令被中断");
        }
    }

    /**
     * 生成项目目录名
     */
    private String generateProjectDirectory(Long projectId) {
        return "project-" + projectId;
    }

    /**
     * 递归删除目录
     */
    private void deleteDirectory(File directory) throws IOException {
        if (!directory.exists()) {
            return;
        }

        if (directory.isDirectory()) {
            File[] files = directory.listFiles();
            if (files != null) {
                for (File file : files) {
                    deleteDirectory(file);
                }
            }
        }

        if (!directory.delete()) {
            throw new IOException("无法删除文件: " + directory.getAbsolutePath());
        }
    }

    /**
     * 从 GitHub URL 提取仓库名称
     * 例如: https://github.com/user/repo.git -> repo
     */
    public String extractRepoName(String repositoryUrl) {
        if (!StringUtils.hasText(repositoryUrl)) {
            return "unknown";
        }

        // 移除 .git 后缀
        String url = repositoryUrl.endsWith(".git")
            ? repositoryUrl.substring(0, repositoryUrl.length() - 4)
            : repositoryUrl;

        // 提取最后一个 / 后的部分
        int lastSlash = url.lastIndexOf('/');
        return lastSlash >= 0 ? url.substring(lastSlash + 1) : url;
    }
}
