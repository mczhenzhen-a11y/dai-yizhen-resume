# 简历库 GitHub 仓库设计方案（v1）

> 用途：把 30 版简历 + 39 份配套报告统一托管到一个公开 GitHub 仓库，**让 ima 知识库能用 `import_urls` 路径批量自动入库**，免去手动粘贴。
> 设计日期：2026-10-10
> 仓库命名建议：`dai-yizhen-resume`（用户名 / 组织名待定）

---

## 一、仓库目标

| 目标 | 说明 |
|---|---|
| **统一托管** | 30 版简历 + JD 拆解报告 + 公司情报 + 证据库 + 求职方法论共 **~70 份 md** |
| **公开可访问** | 公开仓库（public），让 ima 服务端能通过 raw.githubusercontent.com 抓取 |
| **结构清晰** | 一目了然的目录树，新加版本只需 1 个 PR |
| **可被脚本接管** | 用 Python 脚本一键生成所有 raw URL，喂给 ima 的 import_urls |

## 二、目录结构（推荐）

```
dai-yizhen-resume/
├── README.md                                # 总览：候选人画像 / 版本矩阵 / 使用说明
├── CHANGELOG.md                             # 版本变更日志
├── .gitignore                               # 排除敏感文件
├── LICENSE                                  # MIT（公开仓库默认）
│
├── scripts/
│   ├── gen_urls.py                          # 生成 raw URL 列表（用于 ima 批量导入）
│   ├── verify_urls.py                       # 验证 raw URL 可访问性
│   └── url-list.txt                         # 脚本生成：每行一个 raw URL
│
├── docs/                                    # 总览 / 方法论 / 求职策略
│   ├── README.md
│   ├── overview.md                          # 项目总览（候选人画像）
│   ├── 作品集制作指南.md
│   ├── 多企业岗位搜索与投递策略报告.md
│   └── AI产品经理能力体系与项目经历调研报告.md
│
├── resumes/                                 # 30 版简历（核心交付）
│   ├── README.md                            # 版本矩阵：岗位 / 匹配度 / 推荐场景
│   ├── 戴易臻_通用PM校招_Y.md
│   ├── 戴易臻_得物App_Z.md
│   ├── 戴易臻_欧尔孚特_AB.md
│   ├── 戴易臻_博智信息_AC.md
│   ├── 戴易臻_凯馨科技_AD.md
│   └── ... 共 30 版
│
├── reports/                                 # JD 拆解与证据矩阵（22 份）
│   ├── README.md                            # 报告索引
│   ├── JD拆解与证据矩阵_通用PM校招.md
│   ├── JD拆解与证据矩阵_得物App.md
│   └── ...
│
├── company/                                 # 公司情报与岗位定制（4 份）
│   ├── README.md
│   ├── 欧尔孚特_公司情报与岗位定制.md
│   ├── 博智信息_公司情报与岗位定制.md
│   └── 凯馨科技_公司情报与岗位定制.md
│
├── evidence/                                # 证据与素材库（6 份）
│   ├── README.md
│   ├── 证据更新总表_SQL_PRD_竞品分析.md
│   ├── 项目经历_一波三折设计过程.md
│   ├── 校园项目经历_获取成果与能力关键词.md
│   ├── 投递岗位数据库建库指南_SQL.md
│   ├── 项目润色报告_中国城市虚拟交互系统设计.md
│   └── 项目说明_AI协作项目介绍.md
│
└── templates/                               # 求职信 / 自我介绍模板
    ├── README.md
    ├── 自我介绍_30秒.md
    ├── 自我介绍_60秒.md
    └── 求职信模板.md
```

## 三、命名规范

| 类型 | 规范 | 示例 |
|---|---|---|
| 简历 | `戴易臻_<公司或方向>_<版本号>.md` | `戴易臻_得物App_Z.md` |
| JD 拆解 | `JD拆解与证据矩阵_<公司或岗位>.md` | `JD拆解与证据矩阵_通用PM校招.md` |
| 公司情报 | `<公司名>_公司情报与岗位定制.md` | `欧尔孚特_公司情报与岗位定制.md` |
| 证据库 | `<主题>_<类型>.md` | `证据更新总表_SQL_PRD_竞品分析.md` |

## 四、URL 模板

GitHub 公开仓库的 raw 文件 URL 格式固定：

```
https://raw.githubusercontent.com/mczhenzhen-a11y/dai-yizhen-resume/main/<路径>
```

示例（仓库属 `mczhenzhen-a11y`，主分支 `main`）：
```
https://raw.githubusercontent.com/mczhenzhen-a11y/dai-yizhen-resume/main/resumes/戴易臻_得物App_Z.md
https://raw.githubusercontent.com/mczhenzhen-a11y/dai-yizhen-resume/main/reports/JD拆解与证据矩阵_得物App.md
```

**注意**：文件名含中文，URL 需用 UTF-8 编码（脚本里 `urllib.parse.quote` 会自动处理）；路径必须是**相对仓库根**的（如 `resumes/xxx.md`），不可混入本机绝对路径（否则会生成 404）。

## 五、隐私保护清单

简历里可能含敏感信息，**入库前必须检查**：

| 风险项 | 处理方式 |
|---|---|
| 手机号（18177218684） | 公开风险低，但建议加 `_public` 后缀版本（公开版） |
| 邮箱（18177218684@163.com） | 同上，建议公开版脱敏 |
| 学校全名（南京林业大学） | 公开 OK，双一流信息是加分项 |
| 身份证 / 银行卡 / 薪资 | **绝对禁止**上传到公开仓库 |
| 融水实习县域具体地址 | 已模糊处理（仅"广西融水"+ 县城市场描述），无敏感风险 |
| 项目作品站酷/小红书链接 | 公开 OK，主动展示作品 |

**建议**：每份简历维护 `_public` 版本（脱敏版）和 `_full` 版本（完整版，仅本地）。

## 六、ima 自动入库 SOP

```
┌─────────────────────────────────────────────────────────────┐
│  本地：维护简历 / 报告                                       │
└─────────────────────────────────────────────────────────────┘
            │
            ▼ git push（每改一次推一次）
┌─────────────────────────────────────────────────────────────┐
│  GitHub：dai-yizhen-resume（public）                        │
│  · 自动暴露 raw.githubusercontent.com 永久 URL              │
└─────────────────────────────────────────────────────────────┘
            │
            ▼ python scripts/gen_urls.py
┌─────────────────────────────────────────────────────────────┐
│  本地：scripts/url-list.txt                                  │
│  · 每行一个 raw URL                                         │
└─────────────────────────────────────────────────────────────┘
            │
            ▼ mcp__ima-mcp__import_urls（每次最多 10 个）
┌─────────────────────────────────────────────────────────────┐
│  ima：「臻臻的知识库」                                      │
│  · 服务端异步抓取 URL → 解析 → 入库                          │
└─────────────────────────────────────────────────────────────┘
```

**批量入库限制**：ima `import_urls` 单次最多 **10 个 URL**——30 版简历至少分 3 批。

## 七、版本管理

| 文档 | 更新时机 |
|---|---|
| `README.md` | 候选人画像或版本号变化时 |
| `resumes/README.md`（版本矩阵） | 任何简历版本新增 / 升级时 |
| `CHANGELOG.md` | 每次版本变更（简历升级、报告新增） |
| `overview.md` | 整体策略或目标岗位方向调整时 |

## 八、仓库初始化操作清单（首次部署）

```bash
# 1. 本地创建仓库
mkdir dai-yizhen-resume && cd dai-yizhen-resume
git init
git checkout -b main

# 2. 复制目录结构 + 模板文件（详见下方"模板文件"章节）

# 3. 首次提交
git add .
git commit -m "初始化：30 版简历 + 39 份报告 + ima 自动入库脚本"
git branch -M main
git remote add origin https://github.com/mczhenzhen-a11y/dai-yizhen-resume.git
git push -u origin main

# 4. 启用 GitHub Pages（可选，用于美化展示）
# Settings → Pages → Branch: main → Save
```

## 九、首次部署后能做哪些自动化

1. **每周自动同步** —— GitHub Actions cron，定时跑 `gen_urls.py` 生成 URL 列表（存入 issue 或 PR）
2. **PR 模板** —— 新增简历版本时，PR 必须更新 `resumes/README.md` 的版本矩阵
3. **CI 检查** —— 每次提交自动跑 `verify_urls.py`，确保所有 raw URL 可访问（防文件名编码问题）
4. **CHANGELOG 自动生成** —— 用 conventional commits + release-please 自动生成 changelog

---

## 十、模板文件清单（5 份，下面分别产出）

| # | 文件 | 用途 |
|---|---|---|
| 1 | `README.md` | 仓库总览（候选人画像 + 版本矩阵 + 使用说明） |
| 2 | `.gitignore` | 排除本地工作区、敏感文件 |
| 3 | `scripts/gen_urls.py` | 生成 raw URL 列表（喂给 ima） |
| 4 | `scripts/verify_urls.py` | 批量验证 raw URL 可访问性 |
| 5 | `ima批量入库SOP.md` | 完整操作手册（含 import_urls 调用示例） |
