package com.codeassistant.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.codeassistant.user.entity.Project;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.util.List;

/**
 * 项目Mapper接口
 *
 * @author Code Assistant Platform
 * @since 2025-11-16
 */
@Mapper
public interface ProjectMapper extends BaseMapper<Project> {

    /**
     * 根据用户ID查询项目列表
     *
     * @param userId 用户ID
     * @return 项目列表
     */
    @Select("SELECT * FROM projects WHERE user_id = #{userId} AND deleted = 0 ORDER BY created_at DESC")
    List<Project> findByUserId(@Param("userId") Long userId);

    /**
     * 根据用户ID和项目名称查询项目
     *
     * @param userId 用户ID
     * @param name 项目名称
     * @return 项目对象
     */
    @Select("SELECT * FROM projects WHERE user_id = #{userId} AND name = #{name} AND deleted = 0 LIMIT 1")
    Project findByUserIdAndName(@Param("userId") Long userId, @Param("name") String name);

    /**
     * 统计用户的项目数量
     *
     * @param userId 用户ID
     * @return 项目数量
     */
    @Select("SELECT COUNT(*) FROM projects WHERE user_id = #{userId} AND deleted = 0")
    long countByUserId(@Param("userId") Long userId);

    /**
     * 更新项目状态
     *
     * @param projectId 项目ID
     * @param status 新状态
     * @return 影响的行数
     */
    @Update("UPDATE projects SET status = #{status}, updated_at = CURRENT_TIMESTAMP WHERE id = #{projectId} AND deleted = 0")
    int updateStatus(@Param("projectId") Long projectId, @Param("status") String status);

    /**
     * 更新索引状态
     *
     * @param projectId 项目ID
     * @param indexStatus 索引状态
     * @return 影响的行数
     */
    @Update("UPDATE projects SET index_status = #{indexStatus}, updated_at = CURRENT_TIMESTAMP WHERE id = #{projectId} AND deleted = 0")
    int updateIndexStatus(@Param("projectId") Long projectId, @Param("indexStatus") String indexStatus);

    /**
     * 更新索引进度
     *
     * @param projectId 项目ID
     * @param totalFiles 总文件数
     * @param indexedFiles 已索引文件数
     * @return 影响的行数
     */
    @Update("UPDATE projects SET total_files = #{totalFiles}, indexed_files = #{indexedFiles}, updated_at = CURRENT_TIMESTAMP WHERE id = #{projectId} AND deleted = 0")
    int updateIndexProgress(@Param("projectId") Long projectId,
                           @Param("totalFiles") Integer totalFiles,
                           @Param("indexedFiles") Integer indexedFiles);
}
