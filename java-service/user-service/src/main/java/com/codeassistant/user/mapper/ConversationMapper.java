package com.codeassistant.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.codeassistant.user.entity.Conversation;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 对话会话 Mapper 接口
 *
 * 提供对 conversations 表的基础 CRUD 能力以及常用查询方法。
 */
@Mapper
public interface ConversationMapper extends BaseMapper<Conversation> {

    /**
     * 根据项目ID查询对话列表
     *
     * @param projectId 项目ID
     * @return 对话列表
     */
    @Select("SELECT * FROM conversations WHERE project_id = #{projectId} AND deleted = 0 ORDER BY created_at DESC")
    List<Conversation> findByProjectId(@Param("projectId") Long projectId);

    /**
     * 根据项目ID和用户ID查询对话列表
     *
     * @param projectId 项目ID
     * @param userId 用户ID
     * @return 对话列表
     */
    @Select("SELECT * FROM conversations WHERE project_id = #{projectId} AND user_id = #{userId} AND deleted = 0 ORDER BY created_at DESC")
    List<Conversation> findByProjectIdAndUserId(@Param("projectId") Long projectId,
                                                @Param("userId") Long userId);
}

