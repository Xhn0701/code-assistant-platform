package com.codeassistant.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.codeassistant.user.entity.Message;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 对话消息 Mapper 接口
 *
 * 提供对 messages 表的基础 CRUD 能力以及常用查询方法。
 */
@Mapper
public interface MessageMapper extends BaseMapper<Message> {

    /**
     * 根据对话ID查询该对话下的所有消息
     *
     * @param conversationId 对话ID
     * @return 消息列表（按创建时间升序排列）
     */
    @Select("SELECT * FROM messages WHERE conversation_id = #{conversationId} AND deleted = 0 ORDER BY created_at ASC")
    List<Message> findByConversationId(@Param("conversationId") String conversationId);

    /**
     * 查询对话下最近的 N 条消息
     *
     * @param conversationId 对话ID
     * @param limit 限制条数
     * @return 消息列表（按创建时间升序排列）
     */
    @Select("SELECT * FROM messages WHERE conversation_id = #{conversationId} AND deleted = 0 ORDER BY created_at DESC LIMIT #{limit}")
    List<Message> findLatestByConversationId(@Param("conversationId") String conversationId,
                                             @Param("limit") int limit);
}

