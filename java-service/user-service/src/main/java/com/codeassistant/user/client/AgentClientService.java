package com.codeassistant.user.client;

import com.codeassistant.user.client.dto.*;
import com.codeassistant.user.common.BusinessException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

/**
 * Agent服务客户端 - 封装对Python Agent服务的调用
 *
 * 功能:
 * 1. 代码索引 (indexRepository)
 * 2. 任务状态查询 (getTaskStatus)
 * 3. 代码问答 (askQuestion)
 * 4. 代码审查 (reviewCode)
 */
@Service
@Slf4j
public class AgentClientService {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${agent-service.url:http://localhost:8000}")
    private String agentServiceUrl;

    public AgentClientService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * 1. 索引代码仓库
     *
     * @param projectId 项目ID
     * @param repositoryPath 仓库路径
     * @return 索引任务响应
     */
    @Retryable(
        value = {RestClientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public IndexResponse indexRepository(Long projectId, String repositoryPath) {
        log.info("调用Agent服务索引代码仓库: projectId={}, path={}", projectId, repositoryPath);

        try {
            String url = agentServiceUrl + "/api/v1/index/repository";

            IndexRequest request = IndexRequest.builder()
                .projectId(projectId)
                .repositoryUrl(repositoryPath)  // 修改字段名匹配 Python API
                .build();

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<IndexRequest> httpEntity = new HttpEntity<>(request, headers);

            ResponseEntity<PythonApiResponse<IndexResponse>> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                httpEntity,
                new ParameterizedTypeReference<PythonApiResponse<IndexResponse>>() {}
            );

            PythonApiResponse<IndexResponse> body = response.getBody();
            if (body == null || !body.isSuccess()) {
                String errorMsg = body != null ? body.getMessage() : "响应为空";
                throw new BusinessException("索引失败: " + errorMsg);
            }

            IndexResponse data = body.getData();
            log.info("索引完成: projectId={}, status={}, files={}/{}",
                data.getProjectId(), data.getStatus(), data.getIndexedFiles(), data.getTotalFiles());
            return data;

        } catch (RestClientException e) {
            log.error("调用Agent服务失败: {}", e.getMessage(), e);
            throw new BusinessException("调用Agent服务失败: " + e.getMessage());
        }
    }

    /**
     * 2. 查询任务状态
     *
     * @param taskId Celery任务ID
     * @return 任务状态
     */
    @Retryable(
        value = {RestClientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 500, multiplier = 2)
    )
    public TaskStatusResponse getTaskStatus(String taskId) {
        log.debug("查询任务状态: taskId={}", taskId);

        try {
            String url = agentServiceUrl + "/api/v1/tasks/status/" + taskId;

            ResponseEntity<PythonApiResponse<TaskStatusResponse>> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                null,
                new ParameterizedTypeReference<PythonApiResponse<TaskStatusResponse>>() {}
            );

            PythonApiResponse<TaskStatusResponse> body = response.getBody();
            if (body == null || !body.isSuccess()) {
                String errorMsg = body != null ? body.getMessage() : "响应为空";
                throw new BusinessException("查询任务状态失败: " + errorMsg);
            }

            return body.getData();

        } catch (RestClientException e) {
            log.error("查询任务状态失败: {}", e.getMessage(), e);
            throw new BusinessException("查询任务状态失败: " + e.getMessage());
        }
    }

    /**
     * 3. 代码问答
     *
     * @param projectId 项目ID
     * @param question 用户问题
     * @param conversationId 会话ID (可选)
     * @return 问答响应
     */
    @Retryable(
        value = {RestClientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public QuestionResponse askQuestion(Long projectId, String question, Long conversationId) {
        log.info("调用Agent服务问答: projectId={}, question={}", projectId, question);

        try {
            String url = agentServiceUrl + "/api/v1/chat/ask";

            QuestionRequest request = QuestionRequest.builder()
                .projectId(projectId)
                .question(question)
                .conversationId(conversationId)
                .build();

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<QuestionRequest> httpEntity = new HttpEntity<>(request, headers);

            ResponseEntity<PythonApiResponse<QuestionResponse>> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                httpEntity,
                new ParameterizedTypeReference<PythonApiResponse<QuestionResponse>>() {}
            );

            PythonApiResponse<QuestionResponse> body = response.getBody();
            if (body == null || !body.isSuccess()) {
                String errorMsg = body != null ? body.getMessage() : "响应为空";
                throw new BusinessException("问答失败: " + errorMsg);
            }

            log.info("问答成功: confidence={}", body.getData().getConfidence());
            return body.getData();

        } catch (RestClientException e) {
            log.error("调用Agent服务问答失败: {}", e.getMessage(), e);
            throw new BusinessException("调用Agent服务问答失败: " + e.getMessage());
        }
    }

    /**
     * 4. 代码审查
     *
     * @param request 审查请求
     * @return 审查任务响应
     */
    @Retryable(
        value = {RestClientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public ReviewResponse reviewCode(ReviewRequest request) {
        log.info("调用Agent服务代码审查: projectId={}, level={}",
            request.getProjectId(), request.getLevel());

        try {
            String url = agentServiceUrl + "/api/v1/review/analyze";

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<ReviewRequest> httpEntity = new HttpEntity<>(request, headers);

            ResponseEntity<PythonApiResponse<ReviewResponse>> response = restTemplate.exchange(
                url,
                HttpMethod.POST,
                httpEntity,
                new ParameterizedTypeReference<PythonApiResponse<ReviewResponse>>() {}
            );

            PythonApiResponse<ReviewResponse> body = response.getBody();
            if (body == null || !body.isSuccess()) {
                String errorMsg = body != null ? body.getMessage() : "响应为空";
                throw new BusinessException("代码审查失败: " + errorMsg);
            }

            log.info("代码审查任务创建成功: taskId={}", body.getData().getTaskId());
            return body.getData();

        } catch (RestClientException e) {
            log.error("调用Agent服务代码审查失败: {}", e.getMessage(), e);
            throw new BusinessException("调用Agent服务代码审查失败: " + e.getMessage());
        }
    }

    /**
     * 查询审查结果
     *
     * @param taskId 任务ID
     * @return 审查报告
     */
    @Retryable(
        value = {RestClientException.class},
        maxAttempts = 3,
        backoff = @Backoff(delay = 500, multiplier = 2)
    )
    public Object getReviewResult(String taskId) {
        log.debug("查询审查结果: taskId={}", taskId);

        try {
            String url = agentServiceUrl + "/api/v1/review/result/" + taskId;

            ResponseEntity<PythonApiResponse<Object>> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                null,
                new ParameterizedTypeReference<PythonApiResponse<Object>>() {}
            );

            PythonApiResponse<Object> body = response.getBody();
            if (body == null || !body.isSuccess()) {
                String errorMsg = body != null ? body.getMessage() : "响应为空";
                throw new BusinessException("查询审查结果失败: " + errorMsg);
            }

            return body.getData();

        } catch (RestClientException e) {
            log.error("查询审查结果失败: {}", e.getMessage(), e);
            throw new BusinessException("查询审查结果失败: " + e.getMessage());
        }
    }
}
