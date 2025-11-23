package com.codeassistant.user.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.codeassistant.user.entity.AsyncTask;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 异步任务 Mapper
 *
 * @author Code Assistant Platform
 * @since 2025-11-21
 */
@Mapper
public interface AsyncTaskMapper extends BaseMapper<AsyncTask> {

    /**
     * 查询所有正在运行的任务
     *
     * @return 运行中的任务列表
     */
    @Select("SELECT * FROM async_tasks WHERE status IN ('PENDING', 'RUNNING') AND deleted = 0 ORDER BY created_at ASC")
    List<AsyncTask> findRunningTasks();
}
