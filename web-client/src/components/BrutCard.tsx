import { ReactNode } from 'react';
import clsx from 'clsx';

interface BrutCardProps {
  children: ReactNode;
  variant?: 'default' | 'yellow' | 'blue';
  className?: string;
}

/**
 * Neo-Brutalism 风格卡片组件
 *
 * 设计特征:
 * - 黑色实线边框(2px)
 * - 大硬阴影(6px 6px)
 * - 无圆角或极小圆角
 * - 纯色背景
 */
export default function BrutCard({
  children,
  variant = 'default',
  className
}: BrutCardProps) {
  const baseClasses = 'brut-card';

  const variantClasses = {
    default: '',
    yellow: 'bg-brut-yellow',
    blue: 'bg-brut-blue text-brut-white'
  };

  return (
    <div className={clsx(
      baseClasses,
      variantClasses[variant],
      className
    )}>
      {children}
    </div>
  );
}
