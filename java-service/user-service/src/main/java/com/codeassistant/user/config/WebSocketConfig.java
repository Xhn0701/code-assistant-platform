package com.codeassistant.user.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

/**
 * WebSocket 配置类
 *
 * 功能:
 * 1. 启用 STOMP 协议的 WebSocket 消息代理
 * 2. 配置消息端点和订阅前缀
 * 3. 支持 SockJS 降级方案 (不支持WebSocket时用长轮询)
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        // 配置消息代理
        // /topic 用于广播 (一对多) - 所有订阅者都收到
        // /queue 用于点对点 (一对一) - 只有特定用户收到
        config.enableSimpleBroker("/topic", "/queue");

        // 客户端发送消息的前缀
        config.setApplicationDestinationPrefixes("/app");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // 注册 STOMP 端点
        // 客户端通过 /ws 建立 WebSocket 连接
        registry.addEndpoint("/ws")
            .setAllowedOrigins("http://localhost:5173", "http://localhost:3000")  // 允许前端跨域
            .withSockJS();  // 启用 SockJS 降级方案 (兼容不支持WebSocket的浏览器)
    }
}
