-- ============================================
-- V4: 为 projects 表添加 local_path 字段
-- ============================================

-- 添加 local_path 字段
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS local_path VARCHAR(1000);

-- 添加注释
COMMENT ON COLUMN projects.local_path IS '项目本地路径 - 克隆或指定的代码路径';

-- 为已存在的项目设置默认值(基于仓库类型)
-- 注意: 对于已存在的项目,需要手动设置或重新索引
UPDATE projects
SET local_path = CONCAT('/tmp/code-assistant/', id, '/')
WHERE local_path IS NULL AND repository_type IN ('GITHUB', 'GITLAB', 'BITBUCKET');
