import { useState } from 'react';
import type { FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BrutButton, BrutInput, BrutCard, BrutContainer } from '../components';
import { authAPI } from '../services/api';
import { useAuthStore } from '../stores/authStore';

/**
 * Neo-Brutalism 风格登录页面
 */
export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const [credential, setCredential] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(credential, password);
      const { accessToken, user } = response.data.data;

      login(user, accessToken);
      navigate('/');
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
        '登录失败,请检查用户名和密码'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-brut-yellow flex items-center justify-center p-4">
      <BrutContainer className="max-w-md">
        <BrutCard variant="default">
          <h1 className="brut-h2 mb-6 text-center">
            CODE ASSISTANT
          </h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            <BrutInput
              label="用户名或邮箱"
              type="text"
              value={credential}
              onChange={(e) => setCredential(e.target.value)}
              placeholder="输入用户名或邮箱"
              required
            />

            <BrutInput
              label="密码"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="输入密码"
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
              {loading ? '登录中...' : '登录'}
            </BrutButton>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm">
              还没有账号?{' '}
              <Link
                to="/register"
                className="font-bold underline hover:no-underline"
              >
                立即注册
              </Link>
            </p>
          </div>
        </BrutCard>
      </BrutContainer>
    </div>
  );
}
