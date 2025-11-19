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
 * 对话会话实体
 *
 * 对应数据库表：conversations
 * 用于存储用户在某个项目下的对话会话元数据。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("conversations")
public class Conversation {

    /**
     * 对话ID - 主键
     * 使用UUID字符串
     */
    @TableId(value = "id", type = IdType.ASSIGN_UUID)
    private String id;

    /**
     * 项目ID
     */
    @TableField("project_id")
    private Long projectId;

    /**
     * 发起该对话的用户ID
     */
    @TableField("user_id")
    private Long userId;

    /**
     * 对话标题
     */
    @TableField("title")
    private String title;

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
}

