-- ============================================
-- V2: 添加项目表
-- ============================================

-- 项目表 (projects)
CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    repository_url VARCHAR(500),
    repository_type VARCHAR(20) DEFAULT 'LOCAL',
    status VARCHAR(20) NOT NULL DEFAULT 'CREATED',
    index_status VARCHAR(20) DEFAULT 'PENDING',
    language VARCHAR(50),
    total_files INTEGER DEFAULT 0,
    indexed_files INTEGER DEFAULT 0,
    last_indexed_at TIMESTAMP,
    deleted INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_project_status CHECK (status IN ('CREATED', 'INDEXING', 'READY', 'ERROR')),
    CONSTRAINT chk_repository_type CHECK (repository_type IN ('GITHUB', 'GITLAB', 'BITBUCKET', 'LOCAL')),
    CONSTRAINT chk_index_status CHECK (index_status IN ('PENDING', 'INDEXING', 'COMPLETED', 'FAILED')),
    CONSTRAINT chk_project_deleted CHECK (deleted IN (0, 1))
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id) WHERE deleted = 0;
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status) WHERE deleted = 0;
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_projects_user_status ON projects(user_id, status) WHERE deleted = 0;

-- 触发器
CREATE TRIGGER trigger_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 注释
COMMENT ON TABLE projects IS '项目表 - 存储用户代码项目信息';
COMMENT ON COLUMN projects.id IS '项目ID - 主键自增';
COMMENT ON COLUMN projects.user_id IS '所属用户ID';
COMMENT ON COLUMN projects.name IS '项目名称';
COMMENT ON COLUMN projects.description IS '项目描述';
COMMENT ON COLUMN projects.repository_url IS '代码仓库URL';
COMMENT ON COLUMN projects.repository_type IS '仓库类型 - GITHUB, GITLAB, BITBUCKET, LOCAL';
COMMENT ON COLUMN projects.status IS '项目状态 - CREATED:已创建, INDEXING:索引中, READY:就绪, ERROR:错误';
COMMENT ON COLUMN projects.index_status IS '索引状态 - PENDING:待索引, INDEXING:索引中, COMPLETED:已完成, FAILED:失败';
COMMENT ON COLUMN projects.language IS '主要编程语言';
COMMENT ON COLUMN projects.total_files IS '总文件数';
COMMENT ON COLUMN projects.indexed_files IS '已索引文件数';
COMMENT ON COLUMN projects.last_indexed_at IS '最后索引时间';
COMMENT ON COLUMN projects.deleted IS '逻辑删除标记';
COMMENT ON COLUMN projects.created_at IS '创建时间';
COMMENT ON COLUMN projects.updated_at IS '更新时间';
