# Claude Code 项目配置整理

本目录包含 5 个本地项目的 Claude Code 配置文件整理，涵盖项目概况、架构、数据流、编码约定和自定义技能。

## 项目清单

| 项目 | 技术栈 | 说明 |
|------|--------|------|
| image-gen-saas | Next.js 16 + Prisma 7 + AI APIs | AI 图片生成 SaaS |
| type-master | Electron 40 + Vite 6 + React 19 | 打字练习桌面应用 |
| quant-engine | Python + pandas + Streamlit | 量化交易引擎 |
| ai-support-group | Next.js 15 + Prisma 6 + SQLite | AI 戒酒支持社区 |
| tishiciyouhua_repo | Expo 54 + React Native + Supabase | 提示词优化工具 |

## 目录结构

```
projects/     — 每个项目的 CLAUDE.md + CODEMAP.md（架构与约定）
skills/       — 自定义 Skills（可复用的任务模板）
rules/        — 项目特有编码规则（从代码中提取的真实约定）
```

## 文件说明

- **CLAUDE.md**: 每个项目的行为契约 — 技术栈、架构、命令、约定
- **CODEMAP.md**: 目录职责 + 数据流图
- **SKILL.md**: 针对特定场景的可复用工作流模板
