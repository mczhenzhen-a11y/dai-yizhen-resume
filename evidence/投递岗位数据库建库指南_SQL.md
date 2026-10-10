# 投递岗位汇总数据库 — 建库与使用指南

> 用途：把"我会 SQL"从简历上的一句话，变成面试官能当场看到的一个真实系统
> 适用：MySQL 8.0+ / 亦可用 SQLite、腾讯文档智能表格、飞书多维表格替代
> 建议命名：`job_tracker`

---

## 一、为什么值得认真做这件事

这是你在 PM 面试里**唯一能拿出"工具产物"的场景**——大多数应届生的数据能力只能靠嘴说，你可以直接打开数据库跑一条查询给面试官看：

```sql
-- 面试现场可跑：按优先级列出待跟进岗位
SELECT company, position, match_score, status, next_follow_up
FROM applications
WHERE status IN ('已投递','待跟进')
ORDER BY match_score DESC, next_follow_up ASC;
```

一句话解释价值：**"我用数据的方式管理自己的求职流程"——这本身就是产品思维。**

---

## 二、建表设计（4 张表）

### 表 1：`companies` — 公司基础表

```sql
CREATE TABLE companies (
    company_id     INT PRIMARY KEY AUTO_INCREMENT,
    company_name   VARCHAR(100) NOT NULL UNIQUE COMMENT '公司名称',
    industry       VARCHAR(50)  COMMENT '所属行业',
    company_size   VARCHAR(30)  COMMENT '公司规模：初创/中型/大厂',
    city           VARCHAR(30)  COMMENT '工作城市',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
) COMMENT='投递公司信息';
```

### 表 2：`positions` — 岗位表（核心）

```sql
CREATE TABLE positions (
    position_id    INT PRIMARY KEY AUTO_INCREMENT,
    company_id     INT NOT NULL COMMENT '关联 companies',
    position_name  VARCHAR(100) NOT NULL COMMENT '岗位名称',
    job_family     VARCHAR(40)  COMMENT '岗位族：产品/设计/运营',
    direction      VARCHAR(40)  COMMENT '业务方向：电商/AI/IoT/中台/零售',
    jd_summary     TEXT         COMMENT 'JD 核心职责摘要',
    keywords       VARCHAR(255) COMMENT 'JD 关键词，逗号分隔',
    education_req  VARCHAR(50)  COMMENT '学历要求',
    salary_range   VARCHAR(30)  COMMENT '薪资区间',
    publish_date   DATE         COMMENT '发布时间',
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
) COMMENT='岗位信息与JD关键词';
```

### 表 3：`match_analysis` — 匹配度分析表

```sql
CREATE TABLE match_analysis (
    analysis_id    INT PRIMARY KEY AUTO_INCREMENT,
    position_id    INT NOT NULL COMMENT '关联 positions',
    resume_version VARCHAR(20)  COMMENT '使用的简历版本，如 Y',
    match_score    DECIMAL(4,1) COMMENT '匹配度 0-100',
    covered_kw     INT          COMMENT '已覆盖关键词数',
    missing_kw     INT          COMMENT '缺失关键词数',
    gap_notes      TEXT         COMMENT '关键缺口说明',
    analysis_date  DATE         COMMENT '评估日期',
    FOREIGN KEY (position_id) REFERENCES positions(position_id)
) COMMENT='JD匹配度评估结果';
```

### 表 4：`applications` — 投递进度表

```sql
CREATE TABLE applications (
    app_id         INT PRIMARY KEY AUTO_INCREMENT,
    position_id    INT NOT NULL COMMENT '关联 positions',
    apply_date     DATE         COMMENT '投递日期',
    channel        VARCHAR(30)  COMMENT '投递渠道：官网/BOSS/内推',
    status         VARCHAR(20)  DEFAULT '待投递'
                   COMMENT '状态：待投递/已投递/笔试/面试/已offer/已拒绝',
    next_follow_up DATE         COMMENT '下次跟进日期',
    notes          TEXT         COMMENT '备注：面试反馈、待补材料等',
    updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP
                   ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(position_id)
) COMMENT='投递进度跟踪';
```

---

## 三、示例数据（用你真实的投递记录替换）

```sql
INSERT INTO companies (company_name, industry, company_size, city) VALUES
('万辰集团', '零售数字化', '中型', '南京'),
('信人智能', 'AI 硬件', '初创', '南京'),
('京东', '电商/供应链', '大厂', '北京'),
('某新锐 SaaS', '企业服务', '初创', '上海');

INSERT INTO positions (company_id, position_name, job_family, direction, keywords, education_req) VALUES
(1, '零售数字化产品经理（校招）', '产品', '零售', 'PRD,竞品分析,会员体系,ToC,ToB,供应链,需求调研', '本科及以上'),
(2, 'AI 原生应用产品经理', '产品', 'AI', 'PRD,VOC数据,Prompt,Agent,AIGC', '本科及以上'),
(3, '技术产品经理（校招）', '产品', '电商', 'PRD,竞品调研,对话式AI,文档撰写,MVP', '本科及以上'),
(4, '产品实习生', '产品', '中台', 'PRD,业务流程,跨部门,原型', '本科及以上');

INSERT INTO match_analysis (position_id, resume_version, match_score, covered_kw, missing_kw, gap_notes) VALUES
(1, 'S', 74.0, 11, 4, 'Axure/墨刀未实操'),
(2, 'U', 78.0, 12, 3, 'AI 产品实操深度待补'),
(3, 'T', 76.0, 10, 4, '技术语境理解需加强'),
(4, 'W', 70.0,  9, 5, '交易链路经验为零');

INSERT INTO applications (position_id, apply_date, channel, status, next_follow_up, notes) VALUES
(1, '2026-09-20', '官网', '已投递', '2026-09-27', '等待初筛'),
(4, '2026-09-21', 'BOSS', '面试',  '2026-09-25', '一面已过，准备二面');
```

---

## 四、6 条实用查询（面试可以直接演示前 3 条）

```sql
-- 1. 投递漏斗：各状态有多少个岗位
SELECT status, COUNT(*) AS cnt
FROM applications
GROUP BY status
ORDER BY cnt DESC;

-- 2. 各简历版本的平均匹配度（找出哪一版最好用）
SELECT m.resume_version,
       ROUND(AVG(m.match_score), 1) AS avg_score,
       COUNT(*) AS used_times
FROM match_analysis m
GROUP BY m.resume_version
ORDER BY avg_score DESC;

-- 3. 高匹配但还没投的岗位（最高价值的行动清单）
SELECT c.company_name, p.position_name, m.match_score, a.status
FROM positions p
JOIN companies c      ON p.company_id = c.company_id
JOIN match_analysis m ON p.position_id = m.position_id
LEFT JOIN applications a ON p.position_id = a.position_id
WHERE m.match_score >= 75
  AND (a.status IS NULL OR a.status = '待投递')
ORDER BY m.match_score DESC;

-- 4. 按行业统计投递密度
SELECT c.industry, COUNT(*) AS applied_cnt
FROM applications a
JOIN positions p ON a.position_id = p.position_id
JOIN companies c ON p.company_id = c.company_id
GROUP BY c.industry;

-- 5. 关键词缺失排行（告诉我下一步该补什么能力）
SELECT p.keywords, m.missing_kw, m.gap_notes
FROM match_analysis m
JOIN positions p ON m.position_id = p.position_id
ORDER BY m.missing_kw DESC;

-- 6. 本周需要跟进的岗位
SELECT c.company_name, p.position_name, a.status, a.next_follow_up
FROM applications a
JOIN positions p ON a.position_id = p.position_id
JOIN companies c ON p.company_id = c.company_id
WHERE a.next_follow_up BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
ORDER BY a.next_follow_up;
```

---

## 五、低门槛替代方案（如果不想装 MySQL）

| 方案 | 优点 | 缺点 |
|------|------|------|
| **腾讯文档智能表格 / 飞书多维表格** | 零安装、手机可用、可视图/仪表盘 | 不算"真的 SQL"，但已经是数据化管理 |
| **SQLite**（推荐折中） | 单文件、一条命令启动、语法与 MySQL 基本一致 | 无图形界面（可用 DB Browser for SQLite） |
| **MySQL + Workbench / Navicat** | 最接近求职中的真实工作环境 | 需要安装配置 |

> **建议**：本地用 SQLite 或 MySQL 建好（真 SQL 练习），同时把数据同步一份到飞书多维表格（面试演示方便）。

---

## 六、如何体现在简历上（已写入 8 个版本）

已采用的表述：

> **SQL**（MySQL 基础查询 / 多表关联 / 建表与数据维护，可独立完成数据提取与分析——**已自建投递岗位汇总数据库并持续维护**）

> **已掌握 SQL，能自主建表、维护并查询「投递岗位汇总数据库」（岗位名称 / 公司 / JD 关键词 / 匹配度 / 投递状态 / 跟进时间）**——用数据方式管理工作流

**面试加分动作**：面试时若被问到数据能力，主动说"我做了个投递数据库，可以直接给您看表结构和查询结果"——比空谈"熟悉 SQL"有效得多。

---

## 七、下一步动作清单

1. **建库**：选 SQLite 或 MySQL，跑上面 4 条 CREATE TABLE
2. **导入真实数据**：把你目前投过的岗位（应该已有 20+ 条）录进去
3. **跑通查询 1–3**，截图保存
4. **导出表结构 + 查询结果截图**（脱敏：删掉联系方式等）
5. **放进作品集**：作为"数据能力 + 产品思维"的独立一页
