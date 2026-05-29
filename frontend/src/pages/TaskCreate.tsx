import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createTask } from '../api/client'
import { scout } from '../styles/scout-theme'

type QuestionType = 'text' | 'multi-select'

interface Question {
  id: string
  question: string
  subtitle?: string
  type: QuestionType
  options?: string[]
  allowCustom?: boolean
  placeholder?: string
}

const QUESTIONS: Question[] = [
  {
    id: 'query',
    question: 'What do you want to investigate?',
    subtitle: 'Describe the competitive landscape you want to understand',
    type: 'text',
    placeholder: 'e.g., Trae 是字节旗下 AI IDE，请分析 AI coding agent 赛道',
  },
  {
    id: 'focus',
    question: 'What aspects matter most to you?',
    subtitle: 'Select all that apply. We\'ll also cover standard competitive dimensions.',
    type: 'multi-select',
    options: [
      'Technical capabilities',
      'Pricing & business model',
      'Target users & personas',
      'Go-to-market strategy',
      'Integration ecosystem',
      'Security & compliance',
    ],
    allowCustom: true,
  },
  {
    id: 'scope',
    question: 'Where should we look?',
    subtitle: 'Geographic scope for the analysis',
    type: 'multi-select',
    options: ['Global', 'North America', 'Europe', 'China', 'APAC'],
    allowCustom: true,
  },
]

const AI_CODING_AGENT_DEMO = {
  industry: 'AI Coding Agent / AI 编程智能体',
  mainProduct: 'Trae',
  competitors: ['Cursor', 'Windsurf', 'GitHub Copilot', 'Claude Code', 'OpenAI Codex', 'Devin'],
  schemaPack: 'ai_coding_agent',
}

const LEGACY_AI_AGENT_DEMO = {
  industry: 'AI Agent',
  mainProduct: 'ChatGPT',
  competitors: ['Claude', 'Gemini', 'Genspark', 'Manus'],
  schemaPack: 'ai_agent',
}

const shouldUseCodingAgentPack = (query: string) => {
  const normalized = query.toLowerCase()
  return [
    'trae',
    'ai ide',
    'ai coding',
    'coding agent',
    'cursor',
    'windsurf',
    'copilot',
    'claude code',
    'codex',
    'devin',
    '编程',
    '代码',
    'ide',
  ].some(keyword => normalized.includes(keyword))
}

export default function TaskCreate() {
  const navigate = useNavigate()
  const [mounted, setMounted] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({})
  const [input, setInput] = useState('')
  const [customInput, setCustomInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  const currentQ = QUESTIONS[currentStep]
  const isMultiSelect = currentQ?.type === 'multi-select'
  const currentAnswer = (answers[currentQ?.id] as string[]) || []

  // 处理选项选择（多选）
  const toggleOption = (option: string) => {
    const current = (answers[currentQ.id] as string[]) || []
    const updated = current.includes(option)
      ? current.filter(o => o !== option)
      : [...current, option]
    setAnswers({ ...answers, [currentQ.id]: updated })
  }

  // 添加自定义选项
  const addCustom = () => {
    if (!customInput.trim()) return
    const current = (answers[currentQ.id] as string[]) || []
    if (!current.includes(customInput.trim())) {
      setAnswers({ ...answers, [currentQ.id]: [...current, customInput.trim()] })
    }
    setCustomInput('')
  }

  // 下一步
  const goNext = () => {
    if (isMultiSelect) {
      // 多选必须至少选一项
      if (currentAnswer.length === 0) return
    } else {
      // 文本必须非空
      if (!input.trim()) return
      setAnswers({ ...answers, [currentQ.id]: input.trim() })
    }

    setIsTransitioning(true)
    setTimeout(() => {
      if (currentStep < QUESTIONS.length - 1) {
        setCurrentStep(currentStep + 1)
        setInput('')
        setCustomInput('')
        setIsTransitioning(false)
      } else {
        startInvestigation()
      }
    }, 300)
  }

  // 上一步
  const goBack = () => {
    if (currentStep > 0) {
      setIsTransitioning(true)
      setTimeout(() => {
        setCurrentStep(currentStep - 1)
        setIsTransitioning(false)
      }, 300)
    }
  }

  // 自动生成任务名称
  const generateTaskName = (): string => {
    const query = (answers.query as string) || ''
    // 提取关键词：取前 40 个字符，或第一句
    const name = query.length > 40 ? query.slice(0, 40) + '...' : query
    return name || 'Untitled investigation'
  }

  // 开始调查
  const startInvestigation = async () => {
    setLoading(true)
    setError(null)

    try {
      const queryText = (answers.query as string) || ''
      const focusText = (answers.focus as string[])?.join(', ')
      const scopeText = (answers.scope as string[])?.join(', ')
      const taskName = generateTaskName()
      const demoConfig = shouldUseCodingAgentPack(queryText)
        ? AI_CODING_AGENT_DEMO
        : LEGACY_AI_AGENT_DEMO

      const task = await createTask({
        industry: focusText
          ? `${demoConfig.industry}; Focus: ${focusText}`
          : demoConfig.industry,
        region: scopeText || 'Global + China',
        main_product: demoConfig.mainProduct,
        competitors: demoConfig.competitors,
        analysis_goal: queryText,
        query: taskName, // 用于显示的简短名称
        data_mode: 'mock',
        schema_pack: demoConfig.schemaPack,
      })

      // 跳转到工作台，带实时流式状态
      navigate(`/workbench/${task.task_id}`, {
        state: { autoStart: true }
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create investigation'
      setError(message)
      setLoading(false)
      setIsTransitioning(false)
    }
  }

  // 键盘提交
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isMultiSelect) {
      e.preventDefault()
      goNext()
    }
    if (e.key === 'Enter' && e.metaKey) {
      goNext()
    }
  }

  // 进度指示
  const progress = ((currentStep + 1) / QUESTIONS.length) * 100

  return (
    <div style={{
      minHeight: '100vh',
      background: scout.bg.base,
      color: scout.text.primary,
      fontFamily: scout.font.sans,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* 顶部极简导航 */}
      <header style={{
        padding: `${scout.space.lg} ${scout.space.xxl}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <span style={{
          fontSize: scout.size.lg,
          fontWeight: scout.weight.semibold,
          letterSpacing: '-0.02em',
        }}>
          Scout
        </span>
        <a href="/tasks" style={{
          fontSize: scout.size.base,
          color: scout.text.secondary,
          textDecoration: 'none',
        }}>
          History
        </a>
      </header>

      {/* 主内容区 - 全屏翻页 */}
      <main style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        padding: scout.space.xxl,
        position: 'relative',
      }}>
        {/* 进度条 */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: scout.accent.steel,
        }}>
          <div style={{
            width: `${progress}%`,
            height: '100%',
            background: scout.accent.cyan,
            transition: 'width 500ms ease',
          }} />
        </div>

        {/* 问题容器 */}
        <div style={{
          width: '100%',
          maxWidth: 800,
          opacity: isTransitioning ? 0 : 1,
          transform: isTransitioning ? 'translateY(20px)' : 'translateY(0)',
          transition: 'all 300ms ease',
        }}>
          {/* 问题标题 */}
          <h1 style={{
            fontSize: scout.size.display,
            fontWeight: scout.weight.medium,
            marginBottom: scout.space.md,
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
          }}>
            {currentQ?.question}
          </h1>

          {currentQ?.subtitle && (
            <p style={{
              fontSize: scout.size.lg,
              color: scout.text.secondary,
              marginBottom: scout.space.xxl,
            }}>
              {currentQ.subtitle}
            </p>
          )}

          {/* 输入区域 */}
          {currentQ?.type === 'text' ? (
            // 大输入框模式
            <div style={{ marginTop: scout.space.xxl }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={currentQ.placeholder}
                autoFocus
                style={{
                  width: '100%',
                  padding: `${scout.space.lg} ${scout.space.xl}`,
                  fontSize: scout.size.xxl,
                  background: scout.bg.surface,
                  border: `2px solid ${scout.accent.steel}`,
                  borderRadius: scout.radius.xl,
                  color: scout.text.primary,
                  outline: 'none',
                  transition: 'border-color 200ms',
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = scout.accent.cyan
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = scout.accent.steel
                }}
              />

              <div style={{
                marginTop: scout.space.xl,
                display: 'flex',
                gap: scout.space.md,
              }}>
                <button
                  onClick={goNext}
                  disabled={!input.trim()}
                  style={{
                    padding: `${scout.space.md} ${scout.space.xxl}`,
                    background: input.trim() ? scout.text.primary : scout.accent.steel,
                    border: 'none',
                    borderRadius: scout.radius.full,
                    color: input.trim() ? scout.bg.base : scout.text.tertiary,
                    fontSize: scout.size.lg,
                    fontWeight: scout.weight.medium,
                    cursor: input.trim() ? 'pointer' : 'not-allowed',
                  }}
                >
                  Continue →
                </button>
              </div>
            </div>
          ) : (
            // 多选模式
            <div style={{ marginTop: scout.space.xxl }}>
              {/* 选项网格 */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: scout.space.md,
                marginBottom: scout.space.xl,
              }}>
                {currentQ?.options?.map((option) => {
                  const isSelected = currentAnswer.includes(option)
                  return (
                    <button
                      key={option}
                      onClick={() => toggleOption(option)}
                      style={{
                        padding: `${scout.space.lg} ${scout.space.xl}`,
                        background: isSelected ? scout.accent.cyanGlow : scout.bg.surface,
                        border: `2px solid ${isSelected ? scout.accent.cyan : scout.accent.steel}`,
                        borderRadius: scout.radius.lg,
                        color: isSelected ? scout.accent.cyan : scout.text.secondary,
                        fontSize: scout.size.lg,
                        textAlign: 'left',
                        cursor: 'pointer',
                        transition: 'all 150ms',
                        display: 'flex',
                        alignItems: 'center',
                        gap: scout.space.md,
                      }}
                    >
                      <span style={{
                        width: 24,
                        height: 24,
                        borderRadius: scout.radius.sm,
                        border: `2px solid ${isSelected ? scout.accent.cyan : scout.accent.steel}`,
                        background: isSelected ? scout.accent.cyan : 'transparent',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}>
                        {isSelected && (
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={scout.bg.base} strokeWidth="3">
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        )}
                      </span>
                      {option}
                    </button>
                  )
                })}
              </div>

              {/* 自定义输入 */}
              {currentQ?.allowCustom && (
                <div style={{
                  display: 'flex',
                  gap: scout.space.md,
                  marginBottom: scout.space.xl,
                }}>
                  <input
                    type="text"
                    value={customInput}
                    onChange={(e) => setCustomInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && addCustom()}
                    placeholder="+ Add custom..."
                    style={{
                      flex: 1,
                      padding: `${scout.space.md} ${scout.space.lg}`,
                      fontSize: scout.size.lg,
                      background: scout.bg.surface,
                      border: `2px solid ${scout.accent.steel}`,
                      borderRadius: scout.radius.lg,
                      color: scout.text.primary,
                      outline: 'none',
                    }}
                  />
                  <button
                    onClick={addCustom}
                    disabled={!customInput.trim()}
                    style={{
                      padding: `${scout.space.md} ${scout.space.lg}`,
                      background: scout.bg.elevated,
                      border: `2px solid ${scout.accent.steel}`,
                      borderRadius: scout.radius.lg,
                      color: customInput.trim() ? scout.text.primary : scout.text.tertiary,
                      fontSize: scout.size.lg,
                      cursor: customInput.trim() ? 'pointer' : 'not-allowed',
                    }}
                  >
                    Add
                  </button>
                </div>
              )}

              {/* 按钮组 */}
              <div style={{
                display: 'flex',
                gap: scout.space.md,
              }}>
                {currentStep > 0 && (
                  <button
                    onClick={goBack}
                    style={{
                      padding: `${scout.space.md} ${scout.space.xl}`,
                      background: 'transparent',
                      border: `2px solid ${scout.accent.steel}`,
                      borderRadius: scout.radius.full,
                      color: scout.text.secondary,
                      fontSize: scout.size.lg,
                      cursor: 'pointer',
                    }}
                  >
                    ← Back
                  </button>
                )}
                <button
                  onClick={goNext}
                  disabled={currentAnswer.length === 0 || loading}
                  style={{
                    padding: `${scout.space.md} ${scout.space.xxl}`,
                    background: currentAnswer.length > 0 ? scout.text.primary : scout.accent.steel,
                    border: 'none',
                    borderRadius: scout.radius.full,
                    color: currentAnswer.length > 0 ? scout.bg.base : scout.text.tertiary,
                    fontSize: scout.size.lg,
                    fontWeight: scout.weight.medium,
                    cursor: currentAnswer.length > 0 && !loading ? 'pointer' : 'not-allowed',
                  }}
                >
                  {loading ? 'Starting...' : currentStep === QUESTIONS.length - 1 ? 'Start Investigation →' : 'Continue →'}
                </button>
              </div>

              {error && (
                <div style={{
                  marginTop: scout.space.lg,
                  color: scout.status.error,
                  fontSize: scout.size.sm,
                }}>
                  {error}
                </div>
              )}
            </div>
          )}
        </div>

        {/* 底部提示 */}
        <div style={{
          position: 'absolute',
          bottom: scout.space.xxl,
          left: 0,
          right: 0,
          textAlign: 'center',
          color: scout.text.tertiary,
          fontSize: scout.size.sm,
        }}>
          {currentStep === 0 ? 'Press Enter to continue' : `${currentAnswer.length} selected`}
        </div>
      </main>
    </div>
  )
}
