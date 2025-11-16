-- ============================================
-- 智能代码助手平台 - 用户服务数据库表
-- ============================================

-- 删除已存在的表（开发环境用）
DROP TABLE IF EXISTS users CASCADE;

-- ============================================
-- 用户表 (users)
-- ============================================
CREATE TABLE users (
    -- 主键ID
    id BIGSERIAL PRIMARY KEY,

    -- 用户基本信息
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),

    -- 用户状态和角色
    status VARCHAR(20) NOT NULL DEFAULT 'INACTIVE',
    role VARCHAR(20) NOT NULL DEFAULT 'USER',

    -- 登录信息
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(50),

    -- 邮箱验证
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verify_token VARCHAR(255),

    -- 逻辑删除标记
    deleted INTEGER NOT NULL DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT chk_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'BANNED')),
    CONSTRAINT chk_role CHECK (role IN ('USER', 'ADMIN')),
    CONSTRAINT chk_deleted CHECK (deleted IN (0, 1))
);

-- ============================================
-- 索引
-- ============================================

-- 用户名索引（唯一）
CREATE UNIQUE INDEX idx_users_username ON users(username) WHERE deleted = 0;

-- 邮箱索引（唯一）
CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE deleted = 0;

-- 状态索引（查询活跃用户）
CREATE INDEX idx_users_status ON users(status) WHERE deleted = 0;

-- 创建时间索引（按注册时间排序）
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- 复合索引：状态 + 角色（管理员查询）
CREATE INDEX idx_users_status_role ON users(status, role) WHERE deleted = 0;

-- ============================================
-- 注释
-- ============================================

COMMENT ON TABLE users IS '用户表 - 存储用户基本信息和认证数据';

COMMENT ON COLUMN users.id IS '用户ID - 主键自增';
COMMENT ON COLUMN users.username IS '用户名 - 唯一，3-50字符';
COMMENT ON COLUMN users.email IS '邮箱 - 唯一，用于登录';
COMMENT ON COLUMN users.password IS '密码 - BCrypt加密存储';
COMMENT ON COLUMN users.nickname IS '昵称 - 显示名称';
COMMENT ON COLUMN users.avatar_url IS '头像URL';
COMMENT ON COLUMN users.status IS '用户状态 - ACTIVE:正常, INACTIVE:未激活, BANNED:已封禁';
COMMENT ON COLUMN users.role IS '用户角色 - USER:普通用户, ADMIN:管理员';
COMMENT ON COLUMN users.last_login_at IS '最后登录时间';
COMMENT ON COLUMN users.last_login_ip IS '最后登录IP';
COMMENT ON COLUMN users.email_verified IS '邮箱验证状态';
COMMENT ON COLUMN users.email_verify_token IS '邮箱验证Token';
COMMENT ON COLUMN users.deleted IS '逻辑删除标记 - 0:未删除, 1:已删除';
COMMENT ON COLUMN users.created_at IS '创建时间';
COMMENT ON COLUMN users.updated_at IS '更新时间';

-- ============================================
-- 触发器：自动更新 updated_at
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 初始化数据（可选）
-- ============================================

-- 插入管理员账号（密码: Admin123!）
-- BCrypt加密后的密码，用于测试
INSERT INTO users (username, email, password, nickname, status, role, email_verified)
VALUES (
    'admin',
    'admin@codeassistant.com',
    '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- Admin123!
    '系统管理员',
    'ACTIVE',
    'ADMIN',
    TRUE
);

-- 插入测试用户（密码: Test123!）
INSERT INTO users (username, email, password, nickname, status, role, email_verified)
VALUES (
    'testuser',
    'test@example.com',
    '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', -- Test123!
    '测试用户',
    'ACTIVE',
    'USER',
    TRUE
);

-- ============================================
-- 验证表创建成功
-- ============================================

SELECT
    tablename,
    schemaname
FROM pg_tables
WHERE tablename = 'users';

SELECT
    COUNT(*) as user_count,
    COUNT(CASE WHEN role = 'ADMIN' THEN 1 END) as admin_count,
    COUNT(CASE WHEN status = 'ACTIVE' THEN 1 END) as active_count
FROM users;
