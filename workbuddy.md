# workbuddy.md · WorkBuddy 开发对话上下文（专项奖励核验）

> 本文件记录使用腾讯 WorkBuddy 智能体开发「麦麦夸我好身材」参赛项目的真实对话上下文，用于核验是否符合 WorkBuddy 联动活动奖励条件。

## 开发时间
2026-10-24（北京时间）

## 使用的 WorkBuddy 能力
- 智能体对话与任务规划（梳理比赛思路、拆解任务、生成项目骨架）
- 工具调用：通过 `ToolSearch` 加载麦当劳 MCP 工具 schema，并用 `DeferExecuteTool` 真实调用 `list-nutrition-foods`、`query-nearby-stores` 进行只读探测
- 联网检索：抓取官方比赛仓库（M-China/mcd-developer-innovation-challenge）README、CONTEST_DECLARATION.md、activityGuidelines.md，核实报名要求、必填文件、排名与奖励规则
- 文件生成：自动产出 CONTEST_DECLARATION.md（官方原文原样）、mcp-config.example.json、skill/skill.md、skill/references/walk-formula.md、src/mcwalkoff.py、src/nutrition.json、README.md、MCP_INTEGRATION.md、examples 等

## 关键决策与发现（由 WorkBuddy 辅助得出）
1. **必填文件差异核验**：对比用户提供的表格与官方《活动规则》，发现规则额外要求 `mcp-config.example.json`（仅环境变量占位符），已补入项目，避免报名失败。
2. **CONTEST_DECLARATION.md 不可改**：从官方仓库抓取原文并原样写入，未做任何改动。
3. **MCP 能力探测结论**：
   - `list-nutrition-foods` 真实返回 `energyKcal`（卡路里）——卡路里数据源确认。
   - `query-nearby-stores` 实际返回 `distance`（到店距离，米）——这是"走多远"可由麦当劳真实数据计算的关键使能点，无需第三方地图；门店经纬度返回为 0，故以 `distance` 为准。
4. **创意方向（第一版）**：用户选定"用套餐卡路里反推该走去哪家店 / 最近店来回几趟"的趣味健康玩法，命名为「麦麦健步」（后续改名为「麦麦健身」，最终改名为「麦麦夸我好身材」）。
5. **创意方向（第二版 · 当前）**：用户要求改为**单一趣味夸张风**——不再区分两种模式，而是用夸张语气：①炫耀最近门店近到离谱（真实 `distance`）②亮出 1–3 个主推套餐热量榜（巨无霸/麦辣鸡腿/安格斯豪华三件套，能量来自 `list-nutrition-foods`）③算出为吃这顿走路消耗的那点卡路里（少得感人）④甩出深蹲/硬拉/卧推/引体等撸铁动作"补作业"（按每下消耗算个数）。已据此重写 skill.md、walk-formula.md、mcwalkoff.py、README.md、MCP_INTEGRATION.md、examples。

## 交付物
- 完整参赛仓库（见本目录），含 5 个官方要求文件 + 源代码（WorkBuddy 技能 + 离线 CLI）。
- 所有餐品/距离数据依赖麦当劳 MCP 实时返回；离线 CLI 使用采样营养表仅作演示。

## 合规性
- 项目未包含任何真实 Token / 密钥，配置仅用 `${MCD_MCP_TOKEN}` 占位符。
- 输出明确标注"非官方产品、不构成专业建议"。

## 项目最终改名（第三版）
6. **最终改名**：用户将项目名由「麦麦健身」(McFit) 改为 **「麦麦夸我好身材」(McPraise)**。
   - 本地目录 `mcd-fitness` → `mcd-praise`；所有文件显示名、英文副标题、README 目录树同步替换（CONTEST_DECLARATION.md 未触碰）。
   - GitHub 仓库 `tojoevan/mcd-fitness` 重命名为 `tojoevan/mcd-praise`，本地重建 git 后 force push 覆盖远程旧版本；仓库描述同步更新。
   - 报名 Issue #1217 标题与正文（项目名称、项目地址）同步更新为「麦麦夸我好身材」/ `https://github.com/tojoevan/mcd-praise`。
