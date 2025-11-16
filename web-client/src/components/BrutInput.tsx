import { InputHTMLAttributes, forwardRef } from 'react';
import clsx from 'clsx';

interface BrutInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

/**
 * Neo-Brutalism 风格输入框组件
 *
 * 设计特征:
 * - 黑色实线边框(2px)
 * - 聚焦时硬阴影变大
 * - 无圆角
 * - 纯白背景
 */
const BrutInput = forwardRef<HTMLInputElement, BrutInputProps>(({
  label,
  error,
  className,
  ...props
}, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block mb-2 font-bold uppercase text-sm">
          {label}
        </label>
      )}
      <input
        ref={ref}
        className={clsx(
          'brut-input',
          error && 'border-brut-red',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-2 text-sm text-brut-red font-bold">
          {error}
        </p>
      )}
    </div>
  );
});

BrutInput.displayName = 'BrutInput';

export default BrutInput;
