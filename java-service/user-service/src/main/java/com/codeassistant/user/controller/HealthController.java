package com.codeassistant.user.controller;

import com.codeassistant.user.common.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * 健康检查控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/health")
@Tag(name = "健康检查", description = "服务健康状态检查接口")
public class HealthController {

    @Autowired(required = false)
    private DataSource dataSource;

    @Autowired(required = false)
    private RedisTemplate<String, Object> redisTemplate;

    /**
     * 基础健康检查
     */
    @GetMapping
    @Operation(summary = "健康检查", description = "检查服务基本状态")
    public Result<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "user-service");
        health.put("version", "1.0.0");
        health.put("timestamp", System.currentTimeMillis());

        return Result.success(health);
    }

    /**
     * 数据库连接检查
     */
    @GetMapping("/db")
    @Operation(summary = "数据库检查", description = "检查数据库连接状态")
    public Result<Map<String, Object>> checkDatabase() {
        Map<String, Object> dbStatus = new HashMap<>();

        try {
            if (dataSource != null) {
                try (Connection connection = dataSource.getConnection()) {
                    boolean valid = connection.isValid(2);
                    dbStatus.put("status", valid ? "connected" : "disconnected");
                    dbStatus.put("database", connection.getCatalog());
                    dbStatus.put("url", connection.getMetaData().getURL());
                }
            } else {
                dbStatus.put("status", "not configured");
            }
        } catch (Exception e) {
            log.error("数据库连接检查失败", e);
            dbStatus.put("status", "error");
            dbStatus.put("error", e.getMessage());
        }

        return Result.success(dbStatus);
    }

    /**
     * Redis连接检查
     */
    @GetMapping("/redis")
    @Operation(summary = "Redis检查", description = "检查Redis连接状态")
    public Result<Map<String, Object>> checkRedis() {
        Map<String, Object> redisStatus = new HashMap<>();

        try {
            if (redisTemplate != null) {
                // 测试写入
                String testKey = "health:check:test";
                String testValue = "OK";
                redisTemplate.opsForValue().set(testKey, testValue, 10, TimeUnit.SECONDS);

                // 测试读取
                Object value = redisTemplate.opsForValue().get(testKey);

                redisStatus.put("status", testValue.equals(value) ? "connected" : "error");
                redisStatus.put("test", "write and read success");
            } else {
                redisStatus.put("status", "not configured");
            }
        } catch (Exception e) {
            log.error("Redis连接检查失败", e);
            redisStatus.put("status", "error");
            redisStatus.put("error", e.getMessage());
        }

        return Result.success(redisStatus);
    }

    /**
     * 完整健康检查
     */
    @GetMapping("/full")
    @Operation(summary = "完整检查", description = "检查服务、数据库、Redis全部状态")
    public Result<Map<String, Object>> fullHealth() {
        Map<String, Object> fullStatus = new HashMap<>();

        // 服务状态
        fullStatus.put("service", "UP");

        // 数据库状态
        Result<Map<String, Object>> dbResult = checkDatabase();
        fullStatus.put("database", dbResult.getData());

        // Redis状态
        Result<Map<String, Object>> redisResult = checkRedis();
        fullStatus.put("redis", redisResult.getData());

        return Result.success(fullStatus);
    }
}
