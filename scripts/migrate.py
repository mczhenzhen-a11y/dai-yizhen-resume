#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
戴易臻简历库 → GitHub 一键迁移脚本 v1
=====================================
功能：
  1. 扫描本地 30 版简历 + 配套报告，按规则分类
  2. 按命名规范重命名简历（戴易臻_<公司>_<版本>.md）
  3. 创建仓库目录结构（resumes / reports / company / evidence / docs / templates / scripts）
  4. 复制模板文件（README / .gitignore / LICENSE / scripts）
  5. git init + 首次 commit
  6. 输出 git remote add + push 命令（不自动执行远程操作）

用法：
  python migrate.py --source . --target ../dai-yizhen-resume [--github-user YOUR_NAME]

设计日期：2026-10-10
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ==================== 配置区 ====================

# 简历重命名映射表（旧名 → 新名）
# 命名规范：戴易臻_<公司或方向>_<版本号>.md
RESUME_RENAME_MAP = {
    "简历_版本A_百度UIAI视觉设计.md":          "戴易臻_百度UIAI_A.md",
    "简历_版本B_阿里体验设计师.md":              "戴易臻_阿里体验_B.md",
    "简历_版本C_工业产品设计.md":                "戴易臻_工业产品_C.md",
    "简历_版本D_视觉设计方向.md":                "戴易臻_视觉设计_D.md",
    "简历_版本E_交互设计方向.md":                "戴易臻_交互设计_E.md",
    "简历_版本F_B站平面视觉设计.md":             "戴易臻_B站平面_F.md",
    "简历_版本G_B站AI视觉方向.md":               "戴易臻_B站AI视觉_G.md",
    "简历_版本H_B站商业化体验设计.md":           "戴易臻_B站商业化_H.md",
    "简历_版本I_小米UIUE实习生.md":              "戴易臻_小米UIUE_I.md",
    "简历_版本J_阿里2027届校招.md":              "戴易臻_阿里校招_J.md",
    "简历_版本K_电商交互设计校招.md":            "戴易臻_电商交互_K.md",
    "简历_版本L_OPPO_ColorOS交互设计.md":        "戴易臻_OPPO_L.md",
    "简历_版本M_麦当劳设计实习生.md":             "戴易臻_麦当劳_M.md",
    "简历_版本N_游戏UI设计.md":                  "戴易臻_游戏UI_N.md",
    "简历_版本O_AI体验设计.md":                  "戴易臻_AI体验_O.md",
    "简历_版本P_AI时代交互设计.md":              "戴易臻_AI时代_P.md",
    "简历_版本Q_产品经理校招.md":                "戴易臻_通用PM_Q.md",
    "简历_版本R_IoT产品助理校招.md":             "戴易臻_IoT产品_R.md",
    "简历_版本S_万辰集团零售数字化产品经理.md":   "戴易臻_万辰_S.md",
    "简历_版本T_京东技术PM校招.md":              "戴易臻_京东技术PM_T.md",
    "简历_版本U_信人智能AI原生应用PM.md":         "戴易臻_信人AI_U.md",
    "简历_版本V_信人智能新媒体内容运营.md":       "戴易臻_信人新媒体_V.md",
    "简历_版本W_交易中台产品实习生.md":           "戴易臻_交易中台_W.md",
    "简历_版本X_快手电商产品.md":                "戴易臻_快手电商_X.md",
    "简历_版本Y_通用PM校招.md":                  "戴易臻_通用PM_Y.md",
    "简历_版本Z_得物App用户端产品.md":           "戴易臻_得物App_Z.md",
    "简历_版本AA_电商新品开发.md":               "戴易臻_电商新品_AA.md",
    "简历_版本AB_欧尔孚特_新品开发.md":          "戴易臻_欧尔孚特_AB.md",
    "简历_版本AC_博智信息_产品.md":              "戴易臻_博智信息_AC.md",
    "简历_版本AD_凯馨科技_B端产品.md":           "戴易臻_凯馨_AD.md",
}

# 公司情报文件 → company/
COMPANY_FILES = [
    "欧尔孚特_公司情报与岗位定制.md",
    "博智信息_公司情报与岗位定制.md",
    "凯馨科技_公司情报与岗位定制.md",
]

# 证据与方法论 → evidence/
EVIDENCE_FILES = [
    "证据更新总表_SQL_PRD_竞品分析.md",
    "项目经历_一波三折设计过程.md",
    "校园项目经历_获取成果与能力关键词.md",
    "投递岗位数据库建库指南_SQL.md",
    "项目润色报告_中国城市虚拟交互系统设计.md",
    "项目说明_AI协作项目介绍.md",
]

# 总览/方法论 → docs/
DOCS_FILES = [
    "overview.md",
    "多企业岗位搜索与投递策略报告.md",
    "AI产品经理能力体系与项目经历调研报告.md",
    "作品集制作指南.md",
    "戴易臻简历证据优化报告.md" if False else "JD简历证据优化报告.md",
    "项目经历定制报告_基于腾讯文档证据.md",
    "ima知识库入库指南_博智信息简历.md",
    "ima批量入库SOP.md",
    "GitHub仓库设计_简历库.md",
    "面试准备_万辰集团PM岗_问题库与作答参考.md",
]

# 这些文件不复制（脚本自身/模板/本地备份）
EXCLUDE_FILES = {
    "gen_urls.py",
    "verify_urls.py",
    "gitignore_template.txt",
    "README_template.md",
    "migrate.py",  # 自身
}

# 报告分类：JD 拆解文件全部进 reports/
def is_jd_report(name: str) -> bool:
    return name.startswith("JD拆解与证据矩阵_") and name.endswith(".md")


# ==================== 核心函数 ====================

def log(msg: str, level: str = "INFO"):
    """打印带颜色和时间的日志"""
    icons = {"INFO": "ℹ️ ", "OK": "✅", "WARN": "⚠️ ", "ERR": "❌", "STEP": "🚀"}
    icon = icons.get(level, "  ")
    print(f"{icon}  {msg}")


def classify_file(filename: str) -> str | None:
    """根据文件名返回目标目录名"""
    if filename in EXCLUDE_FILES:
        return None
    if filename in RESUME_RENAME_MAP:
        return "resumes"
    if filename in COMPANY_FILES:
        return "company"
    if filename in EVIDENCE_FILES:
        return "evidence"
    if filename in DOCS_FILES:
        return "docs"
    if is_jd_report(filename):
        return "reports"
    # 兜底：未分类的 .md 文件 → 暂放 docs（让用户看到再手动调整）
    if filename.endswith(".md"):
        return "docs"
    return None


def safe_copy(src: Path, dst: Path) -> bool:
    """安全复制文件（处理已存在、权限等）"""
    try:
        if dst.exists():
            log(f"覆盖已存在文件：{dst.name}", "WARN")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception as e:
        log(f"复制失败：{src.name} → {dst.name} ({e})", "ERR")
        return False


def create_resumes_readme(target: Path):
    """生成 resumes/README.md 版本矩阵"""
    content = """\
        # 简历版本矩阵

        > 30 版简历按"公司 / 方向 + 版本号"统一命名，按匹配度从高到低排列。

        | # | 文件名 | 岗位方向 | 匹配度 | 关键词覆盖 | 推荐投递场景 |
        |---|---|---|---|---|---|
        | 1 | 戴易臻_欧尔孚特_AB.md | 家居品类新品开发 | 80% 强 | 40%→90% | 跨境家居电商 |
        | 2 | 戴易臻_得物App_Z.md | 得物 App 用户端 PM | 75% 中强 | 55%→85% | Z 世代电商社区 |
        | 3 | 戴易臻_电商新品_AA.md | 品类开发 / 买手 | 75% 中强 | 35%→88% | 通用电商 |
        | 4 | 戴易臻_博智信息_AC.md | B 端 CRM 产品 | 78% 中强 | 40%→88% | ToB SaaS |
        | 5 | 戴易臻_凯馨_AD.md | 数据安全 B 端产品 | 76% 中强 | 35%→85% | ToB 软件 |
        | 6 | 戴易臻_京东技术PM_T.md | 技术型 PM | 中强 | – | 京东系 |
        | 7 | 戴易臻_信人AI_U.md | AI 原生应用 PM | 中强 | – | AI 公司 |
        | 8 | 戴易臻_交易中台_W.md | 交易中台 PM | 中强 | – | 中后台方向 |
        | 9 | 戴易臻_快手电商_X.md | 内容电商产品 | 中 | – | 练手 + 长线 |
        | 10 | 戴易臻_万辰_S.md | 零售数字化 PM | 中 | – | 零售科技 |
        | 11 | 戴易臻_通用PM_Y.md | 通用 PM 母版 | 72% 中强 | 52%→82% | **任意行业 PM 岗底稿** |
        | 12 | 戴易臻_通用PM_Q.md | 通用 PM | 中 | – | 备选 |
        | 13 | 戴易臻_IoT产品_R.md | IoT 产品助理 | 中 | – | 智能硬件 |
        | 14 | 戴易臻_信人新媒体_V.md | 新媒体内容运营 | 中 | – | 内容方向 |
        | 15 | 戴易臻_百度UIAI_A.md | 百度 UI/AI 视觉 | 中 | – | AI 视觉方向 |
        | 16 | 戴易臻_阿里体验_B.md | 阿里体验设计师 | 强 | – | 体验设计岗 |
        | 17 | 戴易臻_工业产品_C.md | 工业产品设计 | 强 | – | 设计岗主推 |
        | 18 | 戴易臻_视觉设计_D.md | 视觉设计方向 | 中 | – | 视觉岗备选 |
        | 19 | 戴易臻_交互设计_E.md | 交互设计方向 | 中 | – | 交互岗备选 |
        | 20 | 戴易臻_B站平面_F.md | B 站平面视觉 | 中 | – | B 站专属 |
        | 21 | 戴易臻_B站AI视觉_G.md | B 站 AI 视觉 | 中 | – | B 站专属 |
        | 22 | 戴易臻_B站商业化_H.md | B 站商业化体验 | 中 | – | B 站专属 |
        | 23 | 戴易臻_小米UIUE_I.md | 小米 UIUE 实习生 | 中 | – | 小米专属 |
        | 24 | 戴易臻_阿里校招_J.md | 阿里 2027 届校招 | 中 | – | 阿里通投 |
        | 25 | 戴易臻_电商交互_K.md | 电商交互设计 | 中 | – | 电商设计 |
        | 26 | 戴易臻_OPPO_L.md | OPPO ColorOS 交互 | 中 | – | OPPO 专属 |
        | 27 | 戴易臻_麦当劳_M.md | 麦当劳设计实习 | 中 | – | 麦当劳专属 |
        | 28 | 戴易臻_游戏UI_N.md | 游戏 UI 设计 | 中 | – | 游戏方向 |
        | 29 | 戴易臻_AI体验_O.md | AI 体验设计 | 中 | – | AI 体验方向 |
        | 30 | 戴易臻_AI时代_P.md | AI 时代交互 | 中 | – | AI 方向 |

        ## 使用建议

        - **首批推荐投递**：前 5 个版本（匹配度最高 / 关键词提升最大）
        - **通用底稿**：版本 Y（通用 PM 母版），可作为任意 PM 岗的微调底稿
        - **设计岗**：版本 B / C 最强，E / D / L 为备选
        - **AI 方向**：版本 O / P / U 优先

        ## 维护说明

        - 任何版本新增 / 升级时，必须更新本 README
        - 简历文件命名严格遵循 `戴易臻_<公司或方向>_<版本号>.md`
        """
    (target / "resumes" / "README.md").write_text(content, encoding="utf-8")
    log("生成 resumes/README.md（30 版矩阵）", "OK")


def create_reports_readme(target: Path, reports_dir: Path):
    """生成 reports/README.md 索引"""
    jd_files = sorted([f.name for f in reports_dir.iterdir() if f.suffix == ".md"])
    lines = ["# JD 拆解与证据矩阵报告索引\n",
             f"> 共 **{len(jd_files)}** 份 JD 拆解报告，每份对应一个目标岗位版本。\n",
             "\n## 报告清单\n"]
    for f in jd_files:
        lines.append(f"- `{f}`")
    lines.append("\n## 阅读顺序建议\n")
    lines.append("- **先读**：版本 Y / Z / AC / AD / AB 的拆解报告（匹配度最高）")
    lines.append("- **后读**：版本 W / T / U 等中强匹配")
    lines.append("- **最后**：早期岗位（J / K / L 等）的拆解报告（练手参考）")

    (target / "reports" / "README.md").write_text("\n".join(lines), encoding="utf-8")
    log(f"生成 reports/README.md（{len(jd_files)} 份索引）", "OK")


def create_company_readme(target: Path):
    """生成 company/README.md"""
    content = f"""\
        # 公司情报与岗位定制报告

        > 已定向调研 3 家企业：欧尔孚特（跨境家居电商）、博智信息（B 端 CRM SaaS）、凯馨科技（数据安全）。

        | 公司 | 行业 | 规模 | 核心产品 | 报告 |
        |---|---|---|---|---|
        | 欧尔孚特 Orford | 跨境家居电商 | 50–150 人 | WLIVE / DEVAISE | `欧尔孚特_公司情报与岗位定制.md` |
        | 博智信息 | 数字化营销 SaaS | 500–999 人 | CRM / 经销商平台 / 渠道进销存 | `博智信息_公司情报与岗位定制.md` |
        | 凯馨科技 | 数据安全 / 隐私合规 | 50 人 + | Data-Tunnel 数据流通 | `凯馨科技_公司情报与岗位定制.md` |

        ## 调研方法

        1. WebSearch 锁定主营业务 + 团队规模 + 客户名单
        2. 公开招聘 JD 反推岗位画像（薪资 / 工具要求 / 工作内容）
        3. 结合候选人能力做匹配度评估
        4. 产出"同频点 / 缺口 / 面试追问预备"三件套

        ## 更新日期

        {datetime.now().strftime("%Y-%m-%d")} · 共 {len(COMPANY_FILES)} 份
        """
    (target / "company" / "README.md").write_text(content, encoding="utf-8")
    log("生成 company/README.md", "OK")


def create_evidence_readme(target: Path):
    """生成 evidence/README.md"""
    content = """\
        # 证据与方法论文档

        > 跨版本复用的证据 + 求职方法论素材

        ## 文档清单

        | 文档 | 用途 |
        |---|---|
        | `证据更新总表_SQL_PRD_竞品分析.md` | 4 项新证据（SQL / PRD / 竞品 / 调研）的跨版本影响总表 |
        | `项目经历_一波三折设计过程.md` | 6 个项目"第一版走偏 → 调整方法 → 跑通"叙事 |
        | `校园项目经历_获取成果与能力关键词.md` | 6 个项目"做了什么 → 产出物 → 能力"速查 |
        | `投递岗位数据库建库指南_SQL.md` | 4 张表 + 6 条查询 SQL |
        | `项目润色报告_中国城市虚拟交互系统设计.md` | 单项目深度润色范例 |
        | `项目说明_AI协作项目介绍.md` | AI 协作工作流记录 |
        """
    (target / "evidence" / "README.md").write_text(content, encoding="utf-8")
    log("生成 evidence/README.md", "OK")


def create_docs_readme(target: Path, docs_dir: Path):
    """生成 docs/README.md"""
    doc_files = sorted([f.name for f in docs_dir.iterdir() if f.suffix == ".md"])
    lines = ["# 总览与方法论文档\n",
             f"> 共 **{len(doc_files)}** 份\n",
             "\n## 文档清单\n"]
    for f in doc_files:
        lines.append(f"- `{f}`")
    lines.append("\n## 阅读建议\n")
    lines.append("- **先读**：`overview.md` —— 候选人画像 + 30 版版本策略")
    lines.append("- **次读**：`多企业岗位搜索与投递策略报告.md` —— 投递策略")
    lines.append("- **后读**：`AI产品经理能力体系与项目经历调研报告.md` —— 行业认知")
    lines.append("- **方法论**：`作品集制作指南.md`")
    lines.append("- **自动化**：`ima批量入库SOP.md` + `GitHub仓库设计_简历库.md`")
    lines.append("- **面试**：`面试准备_万辰集团PM岗_问题库与作答参考.md`")

    (target / "docs" / "README.md").write_text("\n".join(lines), encoding="utf-8")
    log(f"生成 docs/README.md（{len(doc_files)} 份索引）", "OK")


def create_main_readme(target: Path, stats: dict):
    """生成仓库根 README.md"""
    content = f"""\
        # 戴易臻 — 求职简历库

        > 一个公开托管 {stats['total_resumes']} 版简历 + {stats['total_reports']} 份配套报告的仓库。
        > 设计目标：让 ima 知识库能自动批量入库。

        ---

        ## 👤 候选人画像

        | 维度 | 信息 |
        |---|---|
        | **姓名** | 戴易臻 |
        | **毕业** | 2027 届 · 南京林业大学（双一流）· 工业设计 · 本科 |
        | **方向** | 产品经理 / 交互设计 / UIUX 设计 |
        | **核心数据** | 融水实习 198000 元订单（收益 25740 元 / 13%）/ 5 份项目 PRD / 5 份竞品分析 / 200 份问卷数据清洗 |
        | **工具** | Figma / XMind / Rhino / SQL / Axure（上手中） / Photoshop / Illustrator / KeyShot |
        | **语言** | CET-4 469 / CET-6 452 |
        | **到岗** | 可 2026.09 起，每周 5 天全勤，实习 6 个月以上，**明确接受出差** |

        ## 🎯 三向矩阵

        | 方向 | 代表版本 | 强度 |
        |---|---|---|
        | **产品经理** | Y / Z / AC / AD / AB / AA / T / U / W / X / S / Q / R | ⭐⭐⭐⭐ |
        | **交互 / UI 设计** | B / C / D / E / L / I / M | ⭐⭐⭐⭐⭐ |
        | **AI / 新领域** | O / P / U / G / A | ⭐⭐⭐ |

        ## 📚 目录索引

        | 目录 | 内容 | 文件数 |
        |---|---|---|
        | `resumes/` | 简历版本（核心交付） | {stats['total_resumes']} 版 |
        | `reports/` | JD 拆解与证据矩阵 | {stats['total_reports']} 份 |
        | `company/` | 公司情报与岗位定制 | {len(COMPANY_FILES)} 份 |
        | `evidence/` | 证据与方法论 | {len(EVIDENCE_FILES)} 份 |
        | `docs/` | 总览与方法论文档 | {stats['total_docs']} 份 |
        | `templates/` | 求职信 / 自我介绍模板 | （占位） |
        | `scripts/` | URL 生成 / 验证脚本 | 2 份 |

        ## 🚀 快速使用

        ### 1. 浏览简历

        进入 [`resumes/`](./resumes) 目录，按匹配度从高到低排列：
        - **前 5 版**（欧尔孚特 / 得物 / 电商新品 / 博智 / 凯馨）匹配度最高
        - **版本 Y**（戴易臻_通用PM_Y.md）作为任意行业 PM 岗的通用底稿

        ### 2. 配套报告

        - [`reports/`](./reports) —— 每个目标岗位的 JD 拆解 + 证据矩阵
        - [`company/`](./company) —— 已定向调研的 3 家公司情报
        - [`evidence/`](./evidence) —— 跨版本复用的证据 + 方法论

        ### 3. 自动入库 ima 知识库

        ```bash
        # 生成本仓库所有 .md 的 raw URL
        python scripts/gen_urls.py --owner <GitHub 用户名>
        # 把生成的 URL 列表喂给 ima 的 import_urls（每次最多 10 个）
        ```

        详见 [`docs/ima批量入库SOP.md`](./docs/ima批量入库SOP.md)

        ## 📅 更新日志

        见 [`CHANGELOG.md`](./CHANGELOG.md)

        ## 📄 License

        MIT — 简历内容仅供本人求职使用，公开版已做敏感信息脱敏。
        """
    (target / "README.md").write_text(content, encoding="utf-8")
    log("生成 README.md（仓库总览）", "OK")


def create_changelog(target: Path):
    """生成 CHANGELOG.md"""
    content = f"""\
        # 更新日志

        ## v1.0.0 · {datetime.now().strftime("%Y-%m-%d")}

        ### 新增（Initialized）

        - **{len(RESUME_RENAME_MAP)}** 版简历（戴易臻_<公司>_<版本>.md 命名规范）
        - **{len(COMPANY_FILES)}** 份公司情报报告（欧尔孚特 / 博智 / 凯馨）
        - **{len(EVIDENCE_FILES)}** 份证据与方法论文档
        - 仓库目录结构（resumes / reports / company / evidence / docs / scripts）
        - ima 自动入库脚本（`scripts/gen_urls.py` + `scripts/verify_urls.py`）
        - README + .gitignore + LICENSE
        """
    (target / "CHANGELOG.md").write_text(content, encoding="utf-8")
    log("生成 CHANGELOG.md", "OK")


def create_license(target: Path):
    """生成 LICENSE（MIT）"""
    content = f"""\
        MIT License

        Copyright (c) {datetime.now().year} 戴易臻

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.

        注：本仓库包含求职简历与配套报告，**内容仅供戴易臻本人求职使用**，
        转载 / 二次使用请保留原作者署名。
        """
    (target / "LICENSE").write_text(content, encoding="utf-8")
    log("生成 LICENSE（MIT）", "OK")


def create_gitignore(target: Path):
    """生成 .gitignore"""
    content = """\
        # 操作系统
        .DS_Store
        Thumbs.db
        desktop.ini

        # 编辑器
        .vscode/
        .idea/
        *.swp
        *.swo
        *~

        # Python
        __pycache__/
        *.pyc
        *.pyo
        .venv/

        # 本地工作区文件（不入库）
        .workbuddy/
        tmp_*
        *.tmp
        *.bak
        *_backup_*

        # 私有 / 完整版简历（仅本地保留）
        *_full.md
        *_private.md
        *~private~*

        # 脚本生成的 URL 列表
        scripts/url-list.txt

        # 敏感信息（绝对禁止入库）
        *身份证*
        *银行卡*
        *薪资*
        *salary*
        """
    (target / ".gitignore").write_text(content, encoding="utf-8")
    log("生成 .gitignore", "OK")


def git_run(args: list, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    """执行 git 命令"""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if check and result.returncode != 0:
        log(f"git {' '.join(args)} 失败：{result.stderr}", "ERR")
        sys.exit(1)
    return result


def migrate(source: Path, target: Path, github_user: str = None):
    """执行迁移"""
    log("=" * 60, "STEP")
    log("开始迁移：戴易臻简历库 → GitHub 仓库目录", "STEP")
    log("=" * 60, "STEP")
    log(f"源目录：{source}")
    log(f"目标目录：{target}")

    # 1. 校验源目录
    if not source.exists():
        log(f"源目录不存在：{source}", "ERR")
        sys.exit(1)

    # 3. 创建目标目录结构
    log("\n--- 第 1 步：创建仓库目录结构 ---", "STEP")
    target.mkdir(parents=True, exist_ok=True)
    for sub in ["resumes", "reports", "company", "evidence", "docs", "templates", "scripts"]:
        (target / sub).mkdir(exist_ok=True)
    log(f"已创建：{target} + 7 个子目录", "OK")

    # 4. 扫描源文件
    log("\n--- 第 2 步：扫描源文件 ---", "STEP")
    all_md = [f.name for f in source.iterdir() if f.is_file() and f.suffix == ".md"]
    all_py = [f.name for f in source.iterdir() if f.is_file() and f.suffix == ".py"]
    all_txt = [f.name for f in source.iterdir() if f.is_file() and f.suffix == ".txt"]
    log(f"找到 .md 文件：{len(all_md)} 份")
    log(f"找到 .py 文件：{len(all_py)} 份")
    log(f"找到 .txt 文件：{len(all_txt)} 份")

    # 5. 分类并复制
    log("\n--- 第 3 步：按规则分类并复制文件 ---", "STEP")
    classified = {"resumes": 0, "reports": 0, "company": 0, "evidence": 0, "docs": 0, "skipped": 0}
    classified_files = {}  # 用于后面生成 README

    for fname in all_md:
        target_subdir = classify_file(fname)
        if target_subdir is None:
            log(f"跳过：{fname}", "WARN")
            classified["skipped"] += 1
            continue

        src = source / fname

        # 简历需要重命名
        if fname in RESUME_RENAME_MAP:
            dst_name = RESUME_RENAME_MAP[fname]
        else:
            dst_name = fname

        dst = target / target_subdir / dst_name
        if safe_copy(src, dst):
            classified[target_subdir] += 1
            classified_files.setdefault(target_subdir, []).append(dst_name)

    # 复制脚本文件
    for fname in all_py:
        if fname in EXCLUDE_FILES:
            continue
        src = source / fname
        dst = target / "scripts" / fname
        if safe_copy(src, dst):
            log(f"复制脚本：{fname} → scripts/", "OK")

    log(f"\n分类统计：", "OK")
    for k, v in classified.items():
        log(f"  {k}: {v} 份", "OK")

    # 6. 生成各目录 README
    log("\n--- 第 4 步：生成各目录 README ---", "STEP")
    create_resumes_readme(target)
    create_reports_readme(target, target / "reports")
    create_company_readme(target)
    create_evidence_readme(target)
    create_docs_readme(target, target / "docs")

    # 7. 生成仓库根文件
    log("\n--- 第 5 步：生成仓库根文件 ---", "STEP")
    stats = {
        "total_resumes": classified["resumes"],
        "total_reports": classified["reports"],
        "total_docs": classified["docs"],
    }
    create_main_readme(target, stats)
    create_changelog(target)
    create_license(target)
    create_gitignore(target)

    # 8. git 初始化
    log("\n--- 第 6 步：git 初始化 ---", "STEP")
    git_dir = target / ".git"
    if git_dir.exists():
        log(f"检测到已有 git 仓库：{git_dir}", "WARN")
        log("跳过 git init，仅做 add + commit", "WARN")
    else:
        result = git_run(["init", "-b", "main"], cwd=target, check=False)
        if result.returncode != 0:
            git_run(["init"], cwd=target)
            git_run(["checkout", "-b", "main"], cwd=target, check=False)
        log("git init 完成", "OK")

    # 配置 user（如果未设置）
    user_name = subprocess.run(["git", "config", "user.name"], cwd=target, capture_output=True, text=True).stdout.strip()
    if not user_name:
        git_run(["config", "user.name", "戴易臻"], cwd=target)
        git_run(["config", "user.email", "daiyizhen@example.com"], cwd=target)
        log("git config user.name / user.email（默认值，请修改）", "WARN")

    # add + commit
    git_run(["add", "."], cwd=target)
    commit_msg = f"初始化：{classified['resumes']} 版简历 + {classified['reports']} 份 JD 拆解 + {classified['company']} 份公司情报 + ima 自动入库脚本"
    git_run(["commit", "-m", commit_msg], cwd=target)
    log("git commit 完成", "OK")

    # 9. 输出远程仓库配置命令
    log("\n" + "=" * 60, "STEP")
    log("🎉 迁移完成！接下来你只需 2 步即可上线：", "STEP")
    log("=" * 60, "STEP")

    user = github_user or "<你的 GitHub 用户名>"
    print(f"""
    步骤 1：在 GitHub 创建空仓库（不要勾选 README / .gitignore / License）
            仓库名建议：dai-yizhen-resume
            Visibility：Public（公开，ima 才能抓取）

            创建地址：https://github.com/new

    步骤 2：在目标目录执行以下命令：

            cd "{target}"
            git remote add origin https://github.com/{user}/dai-yizhen-resume.git
            git push -u origin main

    步骤 3：验证 ima 自动入库：

            python scripts/gen_urls.py --owner {user}
            # 把生成的 URL 列表（分块，每块 ≤10 个）喂给 ima 的 import_urls
    """)

    # 10. 校验报告
    log("=" * 60, "STEP")
    log("📊 迁移完成报告", "STEP")
    log("=" * 60, "STEP")
    print(f"""
    仓库目录：{target}

    文件分布：
      · README.md / CHANGELOG.md / LICENSE / .gitignore（仓库根）
      · resumes/        ：{classified['resumes']:3d} 份简历 + 1 份 README
      · reports/        ：{classified['reports']:3d} 份 JD 拆解 + 1 份 README
      · company/        ：{classified['company']:3d} 份公司情报 + 1 份 README
      · evidence/       ：{classified['evidence']:3d} 份证据文档 + 1 份 README
      · docs/           ：{classified['docs']:3d} 份方法论文档 + 1 份 README
      · templates/      ：0 份（占位）
      · scripts/        ：2 个 Python 脚本

    总计：{sum(v for k, v in classified.items() if k != 'skipped')} 份文档 + 7 份 README + 4 份仓库配置

    git 状态：已 init + 首次 commit，未 push
    """)

    log("下一步：在 GitHub 新建空仓库后，运行上面步骤 2 的 git push 命令", "INFO")


# ==================== 入口 ====================

def main():
    parser = argparse.ArgumentParser(
        description="戴易臻简历库 → GitHub 一键迁移脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python migrate.py
  python migrate.py --source . --target ../dai-yizhen-resume
  python migrate.py --github-user yizhen-career
        """,
    )
    parser.add_argument(
        "--source",
        default=".",
        help="源目录（默认：当前目录）",
    )
    parser.add_argument(
        "--target",
        default="../dai-yizhen-resume",
        help="目标仓库目录（默认：../dai-yizhen-resume）",
    )
    parser.add_argument(
        "--github-user",
        default=None,
        help="GitHub 用户名（用于生成 push 命令，可后续填）",
    )

    args = parser.parse_args()

    source = Path(args.source).resolve()
    target = Path(args.target).resolve()

    if source == target:
        log("源目录与目标目录不能相同", "ERR")
        sys.exit(1)

    if target.exists() and any(target.iterdir()):
        log(f"目标目录已存在且非空：{target}", "WARN")
        response = input("是否继续？（y/N）：").strip().lower()
        if response != "y":
            log("用户取消", "INFO")
            sys.exit(0)

    migrate(source, target, args.github_user)


if __name__ == "__main__":
    main()