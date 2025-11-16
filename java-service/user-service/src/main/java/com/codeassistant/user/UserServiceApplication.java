package com.codeassistant.user;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

/**
 * 用户服务启动类
 *
 * @author Code Assistant Platform
 * @since 2025-11-15
 */
@SpringBootApplication
@MapperScan("com.codeassistant.user.mapper")
@EnableCaching
public class UserServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);

        String separator = "============================================================";
        System.out.println("\n" + separator);
        System.out.println("🚀 用户服务启动成功！");
        System.out.println(separator);
        System.out.println("📖 Swagger文档: http://localhost:8080/swagger-ui/");
        System.out.println("🔍 健康检查:    http://localhost:8080/api/health");
        System.out.println("💊 Actuator:   http://localhost:8080/actuator/health");
        System.out.println(separator + "\n");
    }
}
