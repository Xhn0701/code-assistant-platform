package com.codeassistant.user.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.ClientHttpRequestFactory;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.retry.annotation.EnableRetry;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;

/**
 * RestTemplate 配置
 *
 * 功能:
 * 1. 配置连接超时和读取超时
 * 2. 启用重试机制
 * 3. 统一错误处理
 */
@Configuration
@EnableRetry
@Slf4j
public class RestTemplateConfig {

    /**
     * 创建 RestTemplate Bean
     *
     * @param builder RestTemplate构建器
     * @return RestTemplate实例
     */
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .setConnectTimeout(Duration.ofSeconds(10))    // 连接超时: 10秒
            .setReadTimeout(Duration.ofSeconds(30))       // 读取超时: 30秒
            .requestFactory(this::clientHttpRequestFactory)
            .errorHandler(new RestTemplateErrorHandler())
            .build();
    }

    /**
     * 配置 HTTP 请求工厂
     */
    private ClientHttpRequestFactory clientHttpRequestFactory() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(10000);    // 10秒
        factory.setReadTimeout(30000);       // 30秒
        return factory;
    }
}
