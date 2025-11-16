import { ButtonHTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface BrutButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'default' | 'primary' | 'danger' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Neo-Brutalism 风格按钮组件
 *
 * 设计特征:
 * - 黑色实线边框(2px)
 * - 硬阴影(无模糊)
 * - 点击时位移动画
 * - 纯色背景
 */
export default function BrutButton({
  children,
  variant = 'default',
  size = 'md',
  className,
  ...props
}: BrutButtonProps) {
  const baseClasses = 'brut-button cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    default: '',
    primary: 'bg-brut-blue text-brut-white',
    danger: 'bg-brut-red text-brut-white',
    secondary: 'bg-brut-white text-brut-black'
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };

  return (
    <button
      className={clsx(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
