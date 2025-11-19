package com.codeassistant.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.codeassistant.user.entity.CodeReference;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 代码引用 Mapper 接口
 *
 * 提供对 code_references 表的基础 CRUD 能力以及常用查询方法。
 */
@Mapper
public interface CodeReferenceMapper extends BaseMapper<CodeReference> {

    /**
     * 根据消息ID查询其关联的代码引用列表
     *
     * @param messageId 消息ID
     * @return 代码引用列表
     */
    @Select("SELECT * FROM code_references WHERE message_id = #{messageId} AND deleted = 0 ORDER BY start_line NULLS LAST")
    List<CodeReference> findByMessageId(@Param("messageId") Long messageId);
}

