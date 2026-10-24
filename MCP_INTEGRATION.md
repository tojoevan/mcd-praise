# MCP_INTEGRATION.md · 麦当劳 MCP 接入说明

## 一、实际使用的 MCP Server

| 项 | 值 |
|---|---|
| Server 名称 | `mcd-mcp` |
| 传输协议 | `streamablehttp` |
| 接入地址 | `https://mcp.mcd.cn` |
| 鉴权方式 | `Authorization: Bearer <MCD_MCP_TOKEN>`（Token 由麦当劳 MCP 控制台申请） |
| 配置样例 | 见仓库 `mcp-config.example.json`（仅环境变量占位符，无真实密钥） |

> 接入方式遵循官方《WorkBuddy 开发指南》：在 WorkBuddy【自定义连接器】中配置上述 JSON 并启用即可。

## 二、实际调用的 Tool 与用途

| Tool | 用途 | 关键入参 | 关键出参 |
|---|---|---|---|
| `query-nearby-stores` | 按城市+位置关键词查询可点餐门店，**返回 `distance`（到店距离，单位米）** | `beType`(1=到店自取)、`searchType`(2=按位置)、`city`、`keyword` | `storeCode`、`storeName`、`address`、`distance`、`beCode` |
| `list-nutrition-foods` | 获取真实餐品卡路里等营养数据 | 无 | `energyKcal`（能量/kcal）、`energyKj`、`protein`、`fat`、`carbohydrate`、`sodium` 等 |
| `query-meals` | 查询门店餐品列表（用于定价/下单前置） | `storeCode`、`orderType`、`beType` | 餐品及 `code` |
| `calculate-price` | 计算套餐到手价（含优惠） | `storeCode`、`items[].productCode/quantity` | 价格（单位：分，展示÷100） |
| `create-order` *(可选闭环)* | 真实下单 | `storeCode`、`items` 等 | 订单结果 |

> 注：`query-nearby-stores` 的 `distance` 字段是本项目的关键使能点——它让"门店有多近"可由麦当劳真实数据算出，无需接入第三方地图。门店 `longitude/latitude` 在返回中为 0，因此距离以 MCP 返回的 `distance` 为准。

## 三、调用流程（单一趣味玩法）

```
用户意图（"我在<城市><位置>，来点麦当劳"）
  → query-nearby-stores(city, keyword, beType=1, searchType=2)
        # 取带 distance 的门店，挑最近 3 家 → 夸张"近报"
  → list-nutrition-foods
        # 取 energyKcal，挑 1-3 个主推套餐（招牌三件套）或用户指定单品
  → 走路消耗 = 体重 × (2 × 最近店distance/1000) × K
  → 撸铁补作业：剩余 = 套餐kcal − 走路消耗；按每下消耗算各动作个数
  → [可选] query-meals + calculate-price 给到手价，询问是否 create-order
  → 夸张语气输出（门店近报 + 热量榜 + 走路作业 + 撸铁补作业）
```

## 四、业务价值

1. **强传播性（利于 Star 增长）**：夸张反差的表达天然适合截图分享，是大奖排名（纯按 GitHub Star）的核心驱动。
2. **真实数据背书**：卡路里与门店距离全部来自麦当劳官方 MCP，无伪造、无外部依赖，符合活动"真实使用 MCP 能力"要求。
3. **到店转化闭环**：从"算热量"自然过渡到"推荐最近门店 + 到手价 + 一键下单"，把乐子转化为真实到店/自取订单。
4. **双形态交付**：既是 WorkBuddy 技能（对话即服务），也是可运行命令行工具（离线演示），降低评审与用户试用门槛。
