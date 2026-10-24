# 麦麦夸我好身材 (McPraise)

一个**嘴毒心软的麦当劳卡路里课代表**：用麦当劳 MCP 真实数据，先炫耀门店近到离谱，
再亮出主推套餐热量，算出你为了吃这顿走了多少路、烧掉几个卡，最后甩出一组撸铁动作让你"补作业"。
**语气夸张、数字真实**——你吃的每一口，都标好了要还多少深蹲。

> 麦当劳程序员节创意开发大赛参赛作品 · 非官方产品 · 输出仅供参考，不构成专业建议。

---

## 功能亮点

- **门店近报（夸张风）**：基于 `query-nearby-stores` 真实返回的 `distance`（米），炫耀最近麦当劳近到"出门右拐就到"。
- **主推热量榜**：从 `list-nutrition-foods` 真实 `energyKcal` 中取招牌三件套（巨无霸 / 麦辣鸡腿 / 安格斯豪华）热量，构成透明列出。
- **走路作业**：算你为吃这顿走去店里再走回来烧掉的那点卡路里——通常少得感人。
- **撸铁补作业**：用深蹲 / 硬拉 / 卧推 / 引体向上等动作，按每下消耗算出"还欠多少就得做多少个"，制造扎心反差。
- **真实数据驱动**：卡路里与门店距离均来自麦当劳 MCP 实时返回，非硬编码。
- **离线可用**：附带独立命令行工具（`scripts/mcwalkoff.py`），无 MCP 环境也能跑换算演示。

## 目标用户

- 想吃麦当劳又"有罪恶感"、想用运动对冲的年轻人
- 喜欢趣味数据、愿意截图分享传播（利于 GitHub Star）的玩家
- 健身/减脂人群，做"热量账"的轻量乐子工具

---

## 安装与使用

### 方式一：作为 WorkBuddy 技能（推荐，参与 WorkBuddy 专项奖励）

1. 配置麦当劳 MCP 连接器：在 WorkBuddy【连接器】→【自定义连接器】→【配置 MCP】，填入 `mcp-config.example.json` 内容，并将 `${MCD_MCP_TOKEN}` 替换为你的麦当劳 MCP Token。
2. 将本仓库整体放入 WorkBuddy 技能目录（如 `~/.workbuddy/skills/mcd-praise/`），目录内含根级 `SKILL.md`，重启 WorkBuddy 即可在「本地已安装技能」中看到「麦麦夸我好身材」。
3. 直接在对话框描述需求，例如：
   - "我在上海人民广场，给我来点麦当劳的快乐"
   - "附近麦当劳有多近？顺便告诉我巨无霸套餐热量和要撸多少铁"

### 方式二：命令行（离线演示）

```bash
cd scripts
python3 mcwalkoff.py --demo
python3 mcwalkoff.py --nearest-m 144 --stores "华旭国际大厦餐厅,福州路餐厅,食品一店" --weight 60
```

---

## 仓库结构

```
mcd-praise/
├── SKILL.md                   # ★ 技能主体（WorkBuddy 加载，根级）
├── README.md                  # 本文件
├── CONTEST_DECLARATION.md     # 参赛声明（官方原文，不可修改）
├── MCP_INTEGRATION.md         # 麦当劳 MCP 接入说明（Server/Tool/流程/价值）
├── mcp-config.example.json    # 脱敏 MCP 配置（仅环境变量占位符）
├── workbuddy.md               # WorkBuddy 开发对话上下文（专项奖励核验）
├── references/                # 技能参考文档
│   └── walk-formula.md        # 换算公式与撸铁每下消耗
├── scripts/                   # 【源代码】可离线运行的命令行工具
│   ├── mcwalkoff.py
│   └── nutrition.json         # 营养数据采样（实时以 MCP 为准）
└── examples/
    └── example-dialogues.md   # 示例对话
```

## 换算公式（透明可调）

```
走路消耗(kcal) ≈ 体重(kg) × 距离(km) × 系数 K      # 默认 K=0.75、体重 60kg
撸铁补作业：剩余 = 套餐kcal − 走路消耗；动作个数 = ceil(剩余 / 每下消耗)
撸铁每下消耗(粗略)：深蹲0.35 硬拉0.50 卧推0.30 引体0.40 俯卧撑0.25 弯举0.20 kcal/下
```

详见 `references/walk-formula.md`。

## 合规说明

- 本项目为创意开发大赛参赛作品，**非麦当劳官方产品**。
- 餐品、价格、距离、供应状态以麦当劳官方渠道实时结果为准。
- 输出**不构成医疗、营养或运动专业建议**。
- 不存储任何 Token / 密钥；配置文件仅使用环境变量占位符。
