// Scout Theme - 更大字号、更清晰的层级

export const scout = {
  // 背景层级
  bg: {
    base: '#050608',
    surface: '#0A0C10',
    elevated: '#11141A',
    hover: '#181B22',
  },

  // 文字 - 骨白系列
  text: {
    primary: '#F0EEEB',
    secondary: '#9A9590',
    tertiary: '#6A6560',
    quaternary: '#4A4540',
  },

  // 强调色
  accent: {
    cyan: '#00D4AA',
    cyanGlow: 'rgba(0, 212, 170, 0.2)',
    amber: '#E8B87D',
    amberDim: 'rgba(232, 184, 125, 0.15)',
    steel: '#2A2E38',
    steelLight: '#3A3E48',
  },

  // 状态色
  status: {
    ready: '#7CAF6A',
    active: '#00D4AA',
    warning: '#E8B87D',
    error: '#D4847A',
  },

  // 字体
  font: {
    sans: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
    mono: "'SF Mono', 'JetBrains Mono', monospace",
  },

  // 字重
  weight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  // 字号 - 整体放大
  size: {
    xs: '14px',
    sm: '16px',
    base: '18px',
    lg: '22px',
    xl: '28px',
    xxl: '36px',
    xxxl: '48px',
    display: '64px',
  },

  // 间距
  space: {
    xs: '8px',
    sm: '12px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
    xxxl: '64px',
    xxxxl: '96px',
  },

  // 圆角
  radius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px',
  },

  // 过渡
  ease: {
    smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
    snap: 'cubic-bezier(0.16, 1, 0.3, 1)',
  },

  duration: {
    fast: '150ms',
    normal: '300ms',
    slow: '500ms',
  },
};

export const patterns = {
  panel: {
    background: scout.bg.elevated,
    border: `1px solid ${scout.accent.steel}`,
    borderRadius: scout.radius.lg,
  },

  input: {
    background: scout.bg.surface,
    border: `2px solid ${scout.accent.steel}`,
    borderRadius: scout.radius.xl,
    color: scout.text.primary,
    fontSize: scout.size.lg,
    outline: 'none',
  },

  button: {
    primary: {
      background: scout.text.primary,
      color: scout.bg.base,
      padding: `${scout.space.md} ${scout.space.xl}`,
      borderRadius: scout.radius.full,
      fontSize: scout.size.lg,
      fontWeight: scout.weight.medium,
    },
  },
};
