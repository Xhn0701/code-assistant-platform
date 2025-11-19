package com.codeassistant.user.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 对话消息实体
 *
 * 对应数据库表：messages
 * 用于存储会话中的具体消息记录。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("messages")
public class Message {

    /**
     * 消息ID - 主键自增
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 所属对话ID
     */
    @TableField("conversation_id")
    private String conversationId;

    /**
     * 角色
     * user / assistant
     */
    @TableField("role")
    private String role;

    /**
     * 消息内容
     */
    @TableField("content")
    private String content;

    /**
     * 代码引用来源（JSON 字符串）
     * 与数据库中的 JSONB 字段进行映射
     */
    @TableField("sources")
    private String sources;

    /**
     * 逻辑删除标记
     */
    @TableLogic
    @TableField("deleted")
    private Integer deleted;

    /**
     * 创建时间
     */
    @TableField(value = "created_at", fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    @TableField(value = "updated_at", fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;

    /**
     * 消息角色常量
     */
    public static class Role {
        public static final String USER = "user";
        public static final String ASSISTANT = "assistant";
    }
}

