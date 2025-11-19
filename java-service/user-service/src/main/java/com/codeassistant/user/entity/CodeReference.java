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
 * 代码引用实体
 *
 * 对应数据库表：code_references
 * 用于记录每条消息关联的具体代码位置信息。
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@TableName("code_references")
public class CodeReference {

    /**
     * 主键自增ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 关联的消息ID
     */
    @TableField("message_id")
    private Long messageId;

    /**
     * 源代码文件路径（项目内相对路径）
     */
    @TableField("file_path")
    private String filePath;

    /**
     * 代码开始行号
     */
    @TableField("start_line")
    private Integer startLine;

    /**
     * 代码结束行号
     */
    @TableField("end_line")
    private Integer endLine;

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

