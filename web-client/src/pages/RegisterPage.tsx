import { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BrutButton, BrutInput, BrutCard, BrutContainer } from '../components';
import { authAPI } from '../services/api';

/**
 * Neo-Brutalism 风格注册页面
 */
export default function RegisterPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    // 前端验证
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (password.length < 8) {
      setError('密码长度至少为8位');
      return;
    }

    setLoading(true);

    try {
      await authAPI.register(username, email, password);

      // 注册成功后跳转到登录页
      navigate('/login');
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
        '注册失败,请稍后重试'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brut-blue flex items-center justify-center p-4">
      <BrutContainer className="max-w-md">
        <BrutCard variant="default">
          <h1 className="brut-h2 mb-6 text-center">
            创建账号
          </h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            <BrutInput
              label="用户名"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="3-20个字符"
              required
            />

            <BrutInput
              label="邮箱"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />

            <BrutInput
              label="密码"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="至少8位,包含数字和字母"
              required
            />

            <BrutInput
              label="确认密码"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="再次输入密码"
              required
            />

            {error && (
              <div className="p-4 bg-brut-red text-brut-white border-brut border-brut-black shadow-brut-sm">
                <p className="font-bold">{error}</p>
              </div>
            )}

            <BrutButton
              type="submit"
              variant="primary"
              className="w-full"
              disabled={loading}
            >
              {loading ? '注册中...' : '注册'}
            </BrutButton>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm">
              已有账号?{' '}
              <Link
                to="/login"
                className="font-bold underline hover:no-underline"
              >
                立即登录
              </Link>
            </p>
          </div>
        </BrutCard>
      </BrutContainer>
    </div>
  );
}
