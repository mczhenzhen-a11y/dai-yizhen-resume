# ima 知识库批量入库 SOP

> 本文档描述：如何把 GitHub 仓库（dai-yizhen-resume）里的 30 版简历 + 配套报告批量导入到 ima 知识库「臻臻的知识库」。
> 设计日期：2026-10-10
> 适用工具：`mcp__ima-mcp__import_urls`（单次最多 10 个 URL）

---

## 一、前置条件（一次性配置）

### 1. GitHub 仓库已部署

仓库名：`dai-yizhen-resume`
访问性：**public**（公开仓库，ima 服务端才能抓取）
分支：`main`
路径示例：`https://github.com/mczhenzhen-a11y/dai-yizhen-resume`

### 2. 确认 GitHub 用户名

本仓库用户名为 **`mczhenzhen-a11y`**，脚本默认值已内置：
- 仓库地址：`https://github.com/mczhenzhen-a11y/dai-yizhen-resume`

如需换账号，跑脚本时通过 `--owner` 参数指定即可。

### 3. ima 连接器已连接

WorkBuddy 已连接 `ima-mcp` 连接器（个人 ima 账号）。
可写入知识库：「臻臻的知识库」（id `001a966167c03b1f`）。

---

## 二、生成 URL 列表

### 首次 / 全量入库

```bash
# 进入仓库目录
cd dai-yizhen-resume

# 生成所有 .md 文件的 raw URL
python scripts/gen_urls.py --owner mczhenzhen-a11y --repo dai-yizhen-resume --branch main

# 输出：scripts/url-list.txt
# 包含 ~80 个 raw URL，按 10 个一批分块（ima import_urls 单次最多 10 个）
```

### 部分入库（如只入 5 版简历）

```bash
# 只生成 resumes/ 目录下的 URL
python scripts/gen_urls.py --only resumes
```

### 验证 URL 全部可访问

```bash
# 跑一遍 verify_urls.py，确认所有 URL 都能正常访问
python scripts/verify_urls.py

# 输出示例：
#   🔍 验证 80 个 URL（超时 10s，并发 10）...
#   📊 统计：
#      总数：80
#      ✅ 成功（200）：80
#      ❌ 失败：0
#   🎉 所有 URL 可正常访问！
```

**失败处理**：如果部分 URL 404 或 403，先检查：
1. 仓库是否 public（Settings → Danger Zone → Change repository visibility）
2. 文件名编码问题（脚本里已用 `urllib.parse.quote` 处理，但中点 `·` 等特殊字符可能仍有问题）
3. 是否已 push 到 main 分支

---

## 三、批量入库 ima

### 步骤 1：阅读 URL 列表

```bash
cat scripts/url-list.txt
```

输出格式（按 10 个一批分块）：
```
# ─── 批次 1/7（共 10 个）───
https://raw.githubusercontent.com/mczhenzhen-a11y/dai-yizhen-resume/main/docs/overview.md
https://raw.githubusercontent.com/mczhenzhen-a11y/dai-yizhen-resume/main/docs/作品集制作指南.md
...
```

### 步骤 2：逐批调用 import_urls

每批最多 **10 个 URL**。重复以下调用模板 N 次（直到所有批次入库）。

**调用模板**（替换实际 URL）：

```json
{
  "knowledge_base_id": "001a966167c03b1f",
  "folder_id": "",  // 留空 → 入库到根目录
  "urls": [
    "https://raw.githubusercontent.com/mczhenzhen-a11y/dai-yizhen-resume/main/docs/overview.md",
    "https://raw.githubusercontent.com/mczhenzhen-a11y/dai-yizhen-resume/main/resumes/戴易臻_通用PM校招_Y.md",
    ...  // 共 10 个
  ]
}
```

**MCP 调用名称**：`mcp__ima-mcp__import_urls`

**重要**：单次调用最多 10 个 URL。80 个文件 = **至少 8 次调用**。

### 步骤 3：等待异步解析

URL 抓取和解析是异步的（几分钟到几小时不等）。
刚导入就检索往往查不到，**等 5–10 分钟再查**。

### 步骤 4：验证入库结果

```bash
# 抽查某个文件是否入库成功
# 调用：mcp__ima-mcp__search_knowledge
# 参数：knowledge_base_id="001a966167c03b1f", query="博智信息"

# 列出所有入库条目（最近 20 条）
# 调用：mcp__ima-mcp__get_knowledge_list
# 参数：knowledge_base_id="001a966167c03b1f", limit=20, sort_type="UPDATE_TS_DESC_SORT_TYPE"
```

---

## 四、增量更新（简历升级 / 新增时）

简历每次升级都同步到 GitHub → 重新跑脚本 → 入库。

### 工作流

```
┌──────────────────────────────────────────────────────────────┐
│  本地：编辑简历 / 报告                                        │
└──────────────────────────────────────────────────────────────┘
            │ git add . && git commit && git push
            ▼
┌──────────────────────────────────────────────────────────────┐
│  GitHub：dai-yizhen-resume                                   │
└──────────────────────────────────────────────────────────────┘
            │ python scripts/gen_urls.py --only resumes/...
            ▼
┌──────────────────────────────────────────────────────────────┐
│  scripts/url-list.txt（仅包含变更的 URL）                     │
└──────────────────────────────────────────────────────────────┘
            │ 手动筛选出新增/修改的 URL（git diff）
            ▼
┌──────────────────────────────────────────────────────────────┐
│  mcp__ima-mcp__import_urls（仅入库变更的 URL）                │
└──────────────────────────────────────────────────────────────┘
```

**注意**：ima 没有"更新已有条目"的工具——同名文件会被当作**新条目**入库（默认 `SAVE` 策略）。
建议使用 `DUPLICATE_NAME_STRATEGY_REPLACE` 替换已有条目。

```json
{
  "knowledge_base_id": "001a966167c03b1f",
  "urls": ["..."],
  "duplicate_name_strategy": "DUPLICATE_NAME_STRATEGY_REPLACE"
}
```

---

## 五、常见问题

### Q1：URL 含中文文件名会失败吗？

**A**：脚本用 `urllib.parse.quote` 做了 URL 编码，理论上 OK。
但**首次部署后一定要跑 `verify_urls.py` 验证**，避免某个文件编码失败。

### Q2：单次能入多少个 URL？

**A**：ima `import_urls` 单次**最多 10 个**。脚本默认按 10 个分块，80 个文件至少 8 次调用。

### Q3：刚导入查不到怎么办？

**A**：服务端异步解析中，等 5–10 分钟重试。
可用 `get_knowledge_list` + `MEDIA_STATE_FILTER_TYPE` 过滤 `MEDIA_PARSING` 状态，看哪些还在解析中。

### Q4：能不能自动定时跑？

**A**：可以，但需要在 ima 端做，目前 ima-mcp 不支持定时。
**半自动化方案**：用 GitHub Actions 每周跑 `gen_urls.py`，把 URL 列表写到一个公开 URL，再让 AI 工作流每周拉一次喂给 ima。

### Q5：本地工作区文件如何管理？

**A**：建议保留本地原文件，仓库做镜像式托管：
- 本地：C:\Users\33898\WorkBuddy\2026-07-17-09-44-40\（保留所有原文件 + 迭代历史）
- 仓库：dai-yizhen-resume/（仅托管"对外版"——公开的 md 文件）

同步策略：
- 每 2 周一次，从本地复制到仓库（手写脚本或手工）
- 或：用 git submodule 把本地仓库做子模块挂到仓库里（但当前仓库本身就是本地仓库镜像）

### Q6：敏感信息怎么办？

**A**：所有要上传的文件**先过一遍隐私审查清单**：
- [ ] 移除真实身份证号、银行卡号、薪资数字
- [ ] 手机号 / 邮箱**保留**（公开求职常见，不算敏感）
- [ ] 项目作品链接**保留**（主动展示加分）
- [ ] 学校全名**保留**（双一流信息加分）

---

## 六、完整工作流（速查版）

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 本地编辑简历 / 报告
# （用 WorkBuddy 改 C:\Users\33898\WorkBuddy\2026-07-17-09-44-40\ 下的文件）

# 3. 同步到仓库
cp -r ../2026-07-17-09-44-40/*.md dai-yizhen-resume/{resumes,reports,company,evidence,docs}/

# 4. 提交推送
cd dai-yizhen-resume
git add .
git commit -m "升级：xxx"
git push origin main

# 5. 生成 URL
python scripts/gen_urls.py

# 6. 验证 URL
python scripts/verify_urls.py

# 7. 喂给 ima（重复 8 次，每次 10 个 URL）
# 通过 mcp__ima-mcp__import_urls 调用

# 8. 等 5–10 分钟，抽查入库结果
```

---

## 七、自动化进阶（可选）

### GitHub Actions：每周自动生成 URL 列表

`.github/workflows/gen-urls.yml`：

```yaml
name: Generate URL List

on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日 0 点
  workflow_dispatch:       # 支持手动触发

jobs:
  gen-urls:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate URL list
        run: python scripts/gen_urls.py
      - name: Commit URL list
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add scripts/url-list.txt
          git commit -m "自动更新 URL 列表" || echo "无变更"
          git push
```

### CI 检查：每次 push 验证 URL 可访问

`.github/workflows/verify.yml`：

```yaml
name: Verify URLs

on:
  push:
    branches: [main]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Verify all URLs
        run: python scripts/verify_urls.py
```

---

> **总结**：本方案把"手动粘贴简历到 ima"的人工成本，从每次 ~30 分钟降到每次 ~5 分钟（脚本生成 + 7 次 MCP 调用）。**长期复用价值高**——以后任何简历升级都走同一路径。
