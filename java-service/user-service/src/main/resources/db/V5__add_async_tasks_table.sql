-- 创建异步任务表
-- 用于记录后台运行的异步任务 (代码索引、代码审查等)

CREATE TABLE async_tasks (
    id BIGSERIAL PRIMARY KEY,
    project_id BIGINT NOT NULL,
    task_type VARCHAR(20) NOT NULL COMMENT '任务类型: INDEX, REVIEW, CHAT',
    celery_task_id VARCHAR(100) COMMENT 'Celery任务ID',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' COMMENT '任务状态: PENDING, RUNNING, COMPLETED, FAILED',
    progress INTEGER DEFAULT 0 COMMENT '进度百分比 (0-100)',
    message TEXT COMMENT '当前进度描述',
    estimated_time INTEGER COMMENT '预估耗时 (秒)',
    actual_time INTEGER COMMENT '实际耗时 (秒)',
    result JSONB COMMENT '任务结果 (JSON格式)',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted INTEGER NOT NULL DEFAULT 0 COMMENT '逻辑删除标记',
    CONSTRAINT fk_async_tasks_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_async_tasks_project_id ON async_tasks(project_id);
CREATE INDEX idx_async_tasks_status ON async_tasks(status);
CREATE INDEX idx_async_tasks_task_type ON async_tasks(task_type);
CREATE INDEX idx_async_tasks_celery_task_id ON async_tasks(celery_task_id);
CREATE INDEX idx_async_tasks_created_at ON async_tasks(created_at DESC);
CREATE INDEX idx_async_tasks_deleted ON async_tasks(deleted);

-- 添加注释
COMMENT ON TABLE async_tasks IS '异步任务表';
COMMENT ON COLUMN async_tasks.id IS '主键';
COMMENT ON COLUMN async_tasks.project_id IS '关联的项目ID';
COMMENT ON COLUMN async_tasks.task_type IS '任务类型: INDEX(索引), REVIEW(审查), CHAT(问答)';
COMMENT ON COLUMN async_tasks.celery_task_id IS 'Celery任务ID';
COMMENT ON COLUMN async_tasks.status IS '任务状态: PENDING, RUNNING, COMPLETED, FAILED';
COMMENT ON COLUMN async_tasks.progress IS '进度百分比 (0-100)';
COMMENT ON COLUMN async_tasks.message IS '当前进度描述';
COMMENT ON COLUMN async_tasks.estimated_time IS '预估耗时 (秒)';
COMMENT ON COLUMN async_tasks.actual_time IS '实际耗时 (秒)';
COMMENT ON COLUMN async_tasks.result IS '任务结果 (JSON格式)';
COMMENT ON COLUMN async_tasks.error_message IS '错误信息';
COMMENT ON COLUMN async_tasks.created_at IS '创建时间';
COMMENT ON COLUMN async_tasks.updated_at IS '更新时间';
COMMENT ON COLUMN async_tasks.deleted IS '逻辑删除标记';
