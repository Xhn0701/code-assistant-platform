# Frontend Design Specification

## Neo-Brutalism UI Design System

本文档定义了项目前端的设计规范，采用 **Neo-Brutalism（新粗野主义）+ 硬阴影贴纸感** 风格。

---

## 核心技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式**: Tailwind CSS
- **状态管理**: Zustand
- **请求库**: Axios

---

## 设计原则

### 风格定义

Neo-Brutalism 特点：
- **粗犷直接**: 黑色实线边框、无模糊硬阴影
- **高对比度**: 黑白为底，1-2个点缀纯色
- **几何简洁**: 直角或极小圆角，拒绝柔和
- **功能优先**: 清晰的视觉层级，强调可用性

### 设计禁令

**绝对禁止：**
- ❌ 玻璃拟态 (Glassmorphism)
- ❌ 渐变背景
- ❌ 柔和/模糊阴影
- ❌ 大圆角 (超过 4px)
- ❌ 半透明/毛玻璃效果
- ❌ 光晕/发光效果
- ❌ 多色彩低对比的"花屏"感

---

## Design Tokens

### 边框 (Border)

```css
/* 标准边框 - 普通元素 */
border-2 border-black

/* 粗边框 - 重要模块/卡片 */
border-[3px] border-black

/* 细边框 - 次要元素 */
border border-black
```

### 圆角 (Border Radius)

```css
/* 标准圆角 - 几乎所有元素 */
rounded-[2px]

/* 无圆角 - 需要更硬朗的感觉 */
rounded-none

/* 禁止使用 */
/* rounded-lg, rounded-xl, rounded-full 等 */
```

### 阴影 (Shadow)

所有阴影必须是 **无模糊、位移型** 的硬阴影：

```css
/* 小阴影 - 小型组件 */
shadow-[3px_3px_0_0_#000]

/* 中阴影 - 标准卡片/按钮 */
shadow-[6px_6px_0_0_#000]

/* 大阴影 - 强调元素/悬浮状态 */
shadow-[10px_10px_0_0_#000]

/* 交互状态 */
hover:shadow-[10px_10px_0_0_#000]    /* 悬浮增大 */
active:shadow-[4px_4px_0_0_#000]      /* 点击缩小 */
active:translate-x-1 active:translate-y-1  /* 按下位移 */
```

### 配色 (Color Palette)

```css
/* 基础色 - 必须 */
base-white: #FFFFFF
base-black: #000000

/* 点缀色 - 选择 1-2 个 */
accent-yellow: #FFE066    /* 酸性黄 - 推荐主点缀 */
accent-cyan: #67E8F9      /* 青色 */
accent-green: #86EFAC     /* 酸绿 */
accent-pink: #FCA5A5      /* 番茄粉 */

/* 功能色 */
danger: #F87171          /* 错误/删除 */
success: #86EFAC         /* 成功 */
warning: #FBBF24         /* 警告 */

/* 中性色 */
gray-light: #F3F4F6      /* 背景 */
gray-medium: #9CA3AF     /* 次要文本 */
gray-dark: #4B5563       /* 辅助文本 */
```

**对比度要求**: 所有文本必须满足 WCAG AA 标准（至少 4.5:1）

### 排版 (Typography)

```css
/* 大标题 - Black 字重 + 大写 */
font-black text-4xl uppercase tracking-wide

/* 小标题 */
font-bold text-xl uppercase

/* 正文 */
font-medium text-base

/* 数字/代码 - 等宽字体 */
font-mono tabular-nums

/* 链接 */
underline underline-offset-4 decoration-2 hover:decoration-4
```

### 焦点状态 (Focus)

```css
/* 标准焦点环 - 可见且明确 */
focus:outline-none focus:ring-0
focus-visible:border-4 focus-visible:border-black

/* 或使用 ring */
focus-visible:ring-4 focus-visible:ring-black focus-visible:ring-offset-2
```

---

## 基础组件规范

### BrutButton - 按钮

```tsx
interface BrutButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

// 主要按钮
<button className="
  bg-[#FFE066]
  border-[3px] border-black
  rounded-[2px]
  shadow-[6px_6px_0_0_#000]
  px-6 py-3
  font-bold uppercase tracking-wide
  transition-all duration-150
  hover:shadow-[10px_10px_0_0_#000]
  hover:-translate-x-1 hover:-translate-y-1
  active:shadow-[4px_4px_0_0_#000]
  active:translate-x-0 active:translate-y-0
  focus:outline-none focus-visible:border-4
  disabled:opacity-50 disabled:cursor-not-allowed
">
  CLICK ME
</button>

// 次要按钮
<button className="
  bg-white
  border-2 border-black
  rounded-[2px]
  shadow-[4px_4px_0_0_#000]
  px-4 py-2
  font-medium
  hover:shadow-[6px_6px_0_0_#000]
  active:shadow-[2px_2px_0_0_#000]
">
  Secondary
</button>

// 危险按钮
<button className="
  bg-[#F87171] text-white
  border-[3px] border-black
  rounded-[2px]
  shadow-[6px_6px_0_0_#000]
  font-bold uppercase
">
  DELETE
</button>
```

### BrutCard - 卡片

```tsx
<div className="
  bg-white
  border-[3px] border-black
  rounded-[2px]
  shadow-[6px_6px_0_0_#000]
  p-6
">
  <h3 className="font-black text-xl uppercase mb-4">
    CARD TITLE
  </h3>
  <p className="font-medium text-gray-700">
    Card content goes here.
  </p>
</div>
```

### BrutInput - 输入框

```tsx
<input
  type="text"
  className="
    w-full
    bg-white
    border-2 border-black
    rounded-[2px]
    px-4 py-3
    font-medium
    placeholder:text-gray-500
    focus:outline-none
    focus-visible:border-[3px]
    focus-visible:shadow-[4px_4px_0_0_#000]
  "
  placeholder="Enter text..."
/>
```

### BrutTag - 标签

```tsx
// 状态标签
<span className="
  inline-block
  bg-[#86EFAC]
  border-2 border-black
  rounded-[2px]
  shadow-[3px_3px_0_0_#000]
  px-3 py-1
  font-bold text-sm uppercase
">
  ACTIVE
</span>

// 分类标签
<span className="
  inline-block
  bg-[#67E8F9]
  border-2 border-black
  rounded-[2px]
  px-2 py-0.5
  font-medium text-xs uppercase
">
  REACT
</span>
```

### KpiCard - 数据卡片

```tsx
<div className="
  bg-white
  border-[3px] border-black
  rounded-[2px]
  shadow-[6px_6px_0_0_#000]
  p-6
  text-center
">
  <div className="font-mono text-4xl font-black tabular-nums">
    1,234
  </div>
  <div className="font-bold text-sm uppercase mt-2 text-gray-600">
    TOTAL USERS
  </div>
</div>
```

### BrutPanel - 面板

```tsx
<div className="
  bg-[#F3F4F6]
  border-[3px] border-black
  rounded-[2px]
  shadow-[10px_10px_0_0_#000]
  p-8
">
  <header className="
    border-b-[3px] border-black
    pb-4 mb-6
  ">
    <h2 className="font-black text-2xl uppercase">
      PANEL HEADER
    </h2>
  </header>
  <main>
    {/* Panel content */}
  </main>
</div>
```

### BrutTable - 表格

```tsx
<table className="
  w-full
  border-[3px] border-black
  bg-white
">
  <thead className="bg-black text-white">
    <tr>
      <th className="px-4 py-3 text-left font-bold uppercase">
        NAME
      </th>
      <th className="px-4 py-3 text-right font-bold uppercase font-mono">
        COUNT
      </th>
    </tr>
  </thead>
  <tbody>
    <tr className="border-b-2 border-black">
      <td className="px-4 py-3 font-medium">Item One</td>
      <td className="px-4 py-3 text-right font-mono tabular-nums">
        1,234
      </td>
    </tr>
  </tbody>
</table>
```

---

## 布局规范

### 页面结构

```tsx
<div className="min-h-screen bg-[#F3F4F6]">
  {/* 导航栏 */}
  <nav className="
    bg-white
    border-b-[3px] border-black
    px-6 py-4
  ">
    <h1 className="font-black text-2xl uppercase">
      CODE ASSISTANT
    </h1>
  </nav>

  {/* 主内容区 */}
  <main className="container mx-auto px-6 py-8">
    {/* 内容 */}
  </main>
</div>
```

### 网格系统

```tsx
/* 使用 Tailwind Grid */
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* 卡片 */}
</div>

/* 侧边栏布局 */
<div className="flex">
  <aside className="
    w-80
    border-r-[3px] border-black
    min-h-screen
    bg-white
  ">
    {/* 侧边栏 */}
  </aside>
  <main className="flex-1 p-6">
    {/* 主内容 */}
  </main>
</div>
```

---

## 交互规范

### 悬浮效果

```css
/* 按钮悬浮 - 阴影增大 + 轻微上移 */
hover:shadow-[10px_10px_0_0_#000]
hover:-translate-x-1 hover:-translate-y-1

/* 卡片悬浮 - 只增大阴影 */
hover:shadow-[10px_10px_0_0_#000]

/* 链接悬浮 - 下划线加粗 */
hover:decoration-4
```

### 点击效果

```css
/* 按钮点击 - 阴影缩小 + 下沉 */
active:shadow-[4px_4px_0_0_#000]
active:translate-x-0 active:translate-y-0

/* 持续时间 */
transition-all duration-150
```

### 禁用状态

```css
disabled:opacity-50
disabled:cursor-not-allowed
disabled:shadow-none
```

### 加载状态

```tsx
<button className="relative">
  <span className={loading ? 'opacity-0' : ''}>
    SUBMIT
  </span>
  {loading && (
    <div className="
      absolute inset-0
      flex items-center justify-center
    ">
      <div className="
        w-5 h-5
        border-[3px] border-black border-t-transparent
        rounded-full
        animate-spin
      " />
    </div>
  )}
</button>
```

---

## 可访问性要求

### 必须遵守

1. **颜色不是唯一状态编码**
   - 错误状态除了红色，还要有图标或文字
   - 成功状态除了绿色，还要有勾选图标

2. **可见焦点环**
   - 所有可交互元素必须有清晰的焦点样式
   - 使用 `focus-visible` 而非 `focus`

3. **键盘可用**
   - 所有功能可通过键盘完成
   - 正确的 Tab 顺序

4. **对比度**
   - 文本对比度至少 4.5:1 (AA标准)
   - 大文本至少 3:1

5. **语义化HTML**
   ```tsx
   <button> // 而非 <div onClick>
   <a href=""> // 而非 <span onClick>
   <label htmlFor=""> // 表单标签关联
   ```

---

## 代码质量要求

### 组件化

- 封装复用组件：`<BrutButton/>`, `<BrutCard/>`, `<BrutInput/>` 等
- 使用 TypeScript 定义 Props 类型
- 组件职责单一

### 命名规范

```tsx
// 组件名：PascalCase
const BrutButton = () => {}

// 样式变量：camelCase
const shadowMd = 'shadow-[6px_6px_0_0_#000]'

// 常量：UPPER_SNAKE_CASE
const ACCENT_YELLOW = '#FFE066'
```

### 样式组织

```tsx
// 推荐：使用变量组织常用样式
const tokens = {
  borderThin: 'border-2 border-black',
  borderThick: 'border-[3px] border-black',
  shadowSm: 'shadow-[3px_3px_0_0_#000]',
  shadowMd: 'shadow-[6px_6px_0_0_#000]',
  shadowLg: 'shadow-[10px_10px_0_0_#000]',
  radius: 'rounded-[2px]',
}

// 使用
<div className={`bg-white ${tokens.borderThick} ${tokens.radius} ${tokens.shadowMd}`}>
```

---

## Do / Don't 检查清单

### ✅ DO

- [x] 黑白为底 + 1-2 点缀纯色
- [x] 直角或 2px 圆角
- [x] 实线粗边框（1-3px）
- [x] 无模糊、只有位移阴影（3/6/10px）
- [x] Uppercase 小标题
- [x] 数字用等宽字体
- [x] 可见焦点环
- [x] 键盘可用
- [x] AA 对比度
- [x] 语义化 HTML

### ❌ DON'T

- [ ] 渐变
- [ ] 玻璃拟态
- [ ] 柔和阴影/光晕
- [ ] 大圆角
- [ ] 灰度过低的浅文本
- [ ] 只靠颜色区分状态
- [ ] 复杂花纹与纹理背景
- [ ] 多色彩 + 低对比的"花屏"感
- [ ] 半透明效果
- [ ] 动画过于复杂

---

## 示例页面

### 登录页

```tsx
const LoginPage = () => {
  return (
    <div className="min-h-screen bg-[#F3F4F6] flex items-center justify-center p-6">
      <div className="
        w-full max-w-md
        bg-white
        border-[3px] border-black
        rounded-[2px]
        shadow-[10px_10px_0_0_#000]
        p-8
      ">
        <h1 className="font-black text-3xl uppercase mb-8 text-center">
          LOGIN
        </h1>

        <div className="space-y-6">
          <div>
            <label className="block font-bold text-sm uppercase mb-2">
              USERNAME
            </label>
            <input
              type="text"
              className="
                w-full
                bg-white
                border-2 border-black
                rounded-[2px]
                px-4 py-3
                font-medium
                focus:outline-none
                focus-visible:border-[3px]
                focus-visible:shadow-[4px_4px_0_0_#000]
              "
            />
          </div>

          <div>
            <label className="block font-bold text-sm uppercase mb-2">
              PASSWORD
            </label>
            <input
              type="password"
              className="
                w-full
                bg-white
                border-2 border-black
                rounded-[2px]
                px-4 py-3
                font-medium
                focus:outline-none
                focus-visible:border-[3px]
                focus-visible:shadow-[4px_4px_0_0_#000]
              "
            />
          </div>

          <button className="
            w-full
            bg-[#FFE066]
            border-[3px] border-black
            rounded-[2px]
            shadow-[6px_6px_0_0_#000]
            px-6 py-4
            font-black text-lg uppercase tracking-wide
            transition-all duration-150
            hover:shadow-[10px_10px_0_0_#000]
            hover:-translate-x-1 hover:-translate-y-1
            active:shadow-[4px_4px_0_0_#000]
            active:translate-x-0 active:translate-y-0
            focus:outline-none focus-visible:border-4
          ">
            SIGN IN
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

## Tailwind 配置

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'accent-yellow': '#FFE066',
        'accent-cyan': '#67E8F9',
        'accent-green': '#86EFAC',
        'accent-pink': '#FCA5A5',
        'danger': '#F87171',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'brut-sm': '3px 3px 0 0 #000',
        'brut-md': '6px 6px 0 0 #000',
        'brut-lg': '10px 10px 0 0 #000',
      },
    },
  },
  plugins: [],
}
```

---

**版本**: v1.0.0
**最后更新**: 2025-11-16
**设计风格**: Neo-Brutalism + 硬阴影贴纸感
