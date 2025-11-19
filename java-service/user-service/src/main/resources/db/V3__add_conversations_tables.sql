-- ============================================
-- V3: 添加对话与消息相关表
-- conversations, messages, code_references
-- ============================================

-- 对话表：存储项目内的对话会话信息
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(50) PRIMARY KEY,
    project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    deleted INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_conversations_deleted CHECK (deleted IN (0, 1))
);

-- 对话表索引
CREATE INDEX IF NOT EXISTS idx_conversations_project_id
    ON conversations(project_id) WHERE deleted = 0;

CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations(user_id) WHERE deleted = 0;

CREATE INDEX IF NOT EXISTS idx_conversations_project_user
    ON conversations(project_id, user_id) WHERE deleted = 0;

-- 对话表触发器：自动更新 updated_at
CREATE TRIGGER trigger_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 消息表：存储对话中的具体消息
CREATE TABLE IF NOT EXISTS messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id VARCHAR(50) NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB,
    deleted INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_messages_role CHECK (role IN ('user', 'assistant')),
    CONSTRAINT chk_messages_deleted CHECK (deleted IN (0, 1))
);

-- 消息表索引
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id) WHERE deleted = 0;

CREATE INDEX IF NOT EXISTS idx_messages_created_at
    ON messages(created_at) WHERE deleted = 0;

-- 消息表触发器：自动更新 updated_at
CREATE TRIGGER trigger_messages_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 代码引用表：存储每条消息关联的具体代码位置信息
CREATE TABLE IF NOT EXISTS code_references (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    deleted INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_code_references_deleted CHECK (deleted IN (0, 1))
);

-- 代码引用表索引
CREATE INDEX IF NOT EXISTS idx_code_references_message_id
    ON code_references(message_id) WHERE deleted = 0;

-- 代码引用表触发器：自动更新 updated_at
CREATE TRIGGER trigger_code_references_updated_at
    BEFORE UPDATE ON code_references
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
