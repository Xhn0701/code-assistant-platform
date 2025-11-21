"""
Pytest 测试固件（Fixtures）

提供可复用的测试数据和环境配置。
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from app.config import Settings, get_settings
from app.models.code import CodeFile


@pytest.fixture(scope="function")
def temp_chroma_dir(tmp_path: Path) -> Generator[str, None, None]:
    """
    为每个测试提供独立的临时 Chroma 目录。

    使用 function scope 确保每个测试相互隔离。
    """
    # 保存原始配置
    original_settings = get_settings()
    original_dir = original_settings.chroma_persist_directory

    # 创建临时目录
    test_dir = str(tmp_path / "chroma_test")
    os.makedirs(test_dir, exist_ok=True)

    # 覆盖配置
    get_settings.cache_clear()  # 清除缓存
    os.environ["CHROMA_PERSIST_DIRECTORY"] = test_dir

    yield test_dir

    # 恢复原始配置
    get_settings.cache_clear()
    os.environ["CHROMA_PERSIST_DIRECTORY"] = original_dir


@pytest.fixture
def sample_java_code_file() -> CodeFile:
    """
    提供一个示例 Java 文件（UserController）。

    用于测试代码分块、索引等功能。
    """
    content = '''package com.example.user.controller;

import org.springframework.web.bind.annotation.*;
import com.example.user.service.UserService;
import com.example.user.model.User;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/login")
    public Result login(@RequestBody LoginRequest request) {
        // 验证用户名密码
        User user = userService.authenticate(request);
        if (user == null) {
            return Result.error("用户名或密码错误");
        }

        // 生成 JWT Token
        String token = jwtTokenProvider.generateToken(user);
        return Result.success(token);
    }

    @GetMapping("/{id}")
    public Result getUserById(@PathVariable Long id) {
        User user = userService.findById(id);
        if (user == null) {
            return Result.error("用户不存在");
        }
        return Result.success(user);
    }
}'''

    return CodeFile(
        project_id=1,
        path="src/main/java/com/example/user/controller/UserController.java",
        language="java",
        content=content.strip(),
        size_bytes=len(content),
    )


@pytest.fixture
def sample_python_code_file() -> CodeFile:
    """
    提供一个示例 Python 文件（FastAPI 路由）。
    """
    content = '''"""
用户认证 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, auth_service: AuthService = Depends()):
    """
    用户登录接口

    Args:
        request: 登录请求（用户名、密码）
        auth_service: 认证服务（依赖注入）

    Returns:
        LoginResponse: 包含 JWT Token
    """
    user = await auth_service.authenticate(request.username, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = auth_service.generate_token(user)
    return LoginResponse(access_token=token, token_type="bearer")


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user
'''

    return CodeFile(
        project_id=2,
        path="app/api/v1/auth.py",
        language="python",
        content=content.strip(),
        size_bytes=len(content),
    )


@pytest.fixture
def sample_long_code_file() -> CodeFile:
    """
    提供一个较长的代码文件（用于测试分块逻辑）。

    模拟一个包含多个方法的 Service 类。
    """
    content = '''public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public User authenticate(String username, String password) {
        User user = userRepository.findByUsername(username);
        if (user == null) {
            return null;
        }

        if (!passwordEncoder.matches(password, user.getPassword())) {
            return null;
        }

        return user;
    }

    public User register(RegisterRequest request) {
        // 检查用户名是否已存在
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new BusinessException("用户名已存在");
        }

        // 检查邮箱是否已存在
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("邮箱已被注册");
        }

        // 创建用户
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setCreateTime(new Date());

        return userRepository.save(user);
    }

    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }

    public User findByUsername(String username) {
        return userRepository.findByUsername(username);
    }

    public List<User> findAll() {
        return userRepository.findAll();
    }

    public User updateUser(Long id, UpdateUserRequest request) {
        User user = findById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }

        if (request.getEmail() != null) {
            user.setEmail(request.getEmail());
        }

        if (request.getNickname() != null) {
            user.setNickname(request.getNickname());
        }

        user.setUpdateTime(new Date());
        return userRepository.save(user);
    }

    public void deleteUser(Long id) {
        User user = findById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }

        userRepository.delete(user);
    }
}'''

    return CodeFile(
        project_id=1,
        path="src/main/java/com/example/user/service/UserService.java",
        language="java",
        content=content.strip(),
        size_bytes=len(content),
    )


@pytest.fixture(scope="session")
def sample_repository_path(tmp_path_factory) -> Path:
    """
    创建一个临时的示例代码仓库（用于集成测试）。

    使用 session scope 避免重复创建。
    """
    repo_dir = tmp_path_factory.mktemp("sample_repo")

    # 创建目录结构
    src_dir = repo_dir / "src" / "main" / "java" / "com" / "example"
    src_dir.mkdir(parents=True, exist_ok=True)

    # 创建示例文件
    (src_dir / "User.java").write_text(
        '''public class User {
    private Long id;
    private String username;
    private String email;

    // Getters and setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
}'''
    )

    (src_dir / "UserService.java").write_text(
        '''public class UserService {
    public User findById(Long id) {
        // Implementation
        return null;
    }
}'''
    )

    # 创建 README
    (repo_dir / "README.md").write_text("# Sample Repository\n\nFor testing purposes.")

    return repo_dir


@pytest.fixture
def mock_openai_embedding_response():
    """
    模拟 OpenAI Embedding API 响应。

    用于不依赖真实 API 的测试。
    """
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1] * 1536,  # text-embedding-3-small 维度
                "index": 0,
            }
        ],
        "model": "text-embedding-3-small",
        "usage": {"prompt_tokens": 10, "total_tokens": 10},
    }


@pytest.fixture
def test_settings() -> Settings:
    """
    提供测试专用的配置。

    覆盖部分配置以适应测试环境。
    """
    get_settings.cache_clear()

    # 设置测试环境变量
    os.environ["DEBUG"] = "true"
    os.environ["INDEX_CHUNK_SIZE"] = "200"
    os.environ["INDEX_CHUNK_OVERLAP"] = "50"
    os.environ["OPENAI_API_KEY"] = "sk-test-key"

    settings = get_settings()

    yield settings

    # 清理
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def setup_chroma_for_integration(temp_chroma_dir: str, request):
    """
    为集成测试自动初始化 ChromaDB 客户端。

    只在 integration 目录下的测试中自动运行。
    """
    # 只对集成测试生效
    if "integration" not in str(request.fspath):
        yield
        return

    from app.services.vectorstore import cleanup_chroma_client, init_chroma_client

    # 清理并重新初始化
    cleanup_chroma_client()
    init_chroma_client()

    yield

    # 测试后清理
    cleanup_chroma_client()
