import type { ReactNode } from 'react';
import clsx from 'clsx';

interface BrutContainerProps {
  children: ReactNode;
  className?: string;
}

/**
 * Neo-Brutalism 风格容器组件
 * 用于页面内容的最大宽度限制和居中
 */
export default function BrutContainer({ children, className }: BrutContainerProps) {
  return (
    <div className={clsx('brut-container', className)}>
      {children}
    </div>
  );
}
