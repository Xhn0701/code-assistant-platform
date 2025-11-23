package com.codeassistant.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

/**
 * 创建项目请求DTO
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateProjectRequest {

    /**
     * 项目名称
     */
    @NotBlank(message = "项目名称不能为空")
    @Size(min = 1, max = 100, message = "项目名称长度必须在1-100个字符之间")
    private String name;

    /**
     * 项目描述
     */
    @Size(max = 1000, message = "项目描述不能超过1000个字符")
    private String description;

    /**
     * 代码仓库URL
     */
    @Size(max = 500, message = "仓库URL不能超过500个字符")
    private String repositoryUrl;

    /**
     * 仓库类型 (GITHUB, GITLAB, BITBUCKET, LOCAL)
     */
    private String repositoryType;

    /**
     * 项目本地路径
     * 对于 LOCAL 类型项目必填，指向本地代码目录
     * 对于远程仓库可选，如果不指定将自动克隆到默认位置
     */
    @Size(max = 1000, message = "本地路径不能超过1000个字符")
    private String localPath;
}
