package com.codeassistant.user.config;

import com.codeassistant.user.common.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.client.ClientHttpResponse;
import org.springframework.web.client.ResponseErrorHandler;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.stream.Collectors;

/**
 * RestTemplate 错误处理器
 *
 * 统一处理 HTTP 错误响应
 */
@Slf4j
public class RestTemplateErrorHandler implements ResponseErrorHandler {

    @Override
    public boolean hasError(ClientHttpResponse response) throws IOException {
        HttpStatus.Series series = response.getStatusCode().series();
        return series == HttpStatus.Series.CLIENT_ERROR ||
               series == HttpStatus.Series.SERVER_ERROR;
    }

    @Override
    public void handleError(ClientHttpResponse response) throws IOException {
        HttpStatus statusCode = response.getStatusCode();
        String statusText = response.getStatusText();

        // 读取响应体
        String responseBody = "";
        try (BufferedReader reader = new BufferedReader(
            new InputStreamReader(response.getBody(), StandardCharsets.UTF_8))) {
            responseBody = reader.lines().collect(Collectors.joining("\n"));
        } catch (Exception e) {
            log.warn("读取错误响应体失败: {}", e.getMessage());
        }

        log.error("HTTP请求失败: status={}, message={}, body={}",
            statusCode, statusText, responseBody);

        // 根据状态码分类处理
        if (statusCode.is4xxClientError()) {
            throw new BusinessException(
                String.format("客户端请求错误 [%d]: %s", statusCode.value(), statusText)
            );
        } else if (statusCode.is5xxServerError()) {
            throw new BusinessException(
                String.format("服务端错误 [%d]: %s", statusCode.value(), statusText)
            );
        } else {
            throw new BusinessException(
                String.format("未知错误 [%d]: %s", statusCode.value(), statusText)
            );
        }
    }
}
