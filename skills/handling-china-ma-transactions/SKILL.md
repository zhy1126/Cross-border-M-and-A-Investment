---
name: handling-china-ma-transactions
description: Use when a China-focused M&A matter requires transaction-structure selection or comparison, including listed-company control acquisitions, staged equity acquisitions, and asset or business acquisitions.
---

# 中国并购交易结构方案规划

## 产品合同

本 Skill 只负责交易结构方案规划。固定流程是：六组输入 → 控制目标 → 路径比较 → 并表证据检验 → 八部分输出、双版本交付与四类后续任务包。

三维决策内核按因果顺序处理：

1. **控制权**：确定目标权力、适用口径和取得时点；
2. **收购方式**：围绕控制目标比较基准、备选、兜底路径；
3. **合并财务报表**：检验前两维形成的事实是否支持会计控制和购买日判断，不代替会计结论。

## 启动与立场

每次先填写 [固定输入模板](assets/matter-intake-template.md)，并按 [入项、路由与门控](references/intake-routing-and-gates.md) 校验六组输入。

- 默认 `Perspective: Buyer`；用户指定卖方时切换为 `Perspective: Seller`。
- 切换立场必须重新评估目标优先级、推荐理由、成立条件、改道触发器和决策请求，不能只替换称谓。
- `start-required` 缺失时停止结构化规划；`recommendation-blocker` 未关闭时可以比较路径，但不得确定推荐，状态为 `blocked`。
- 每一非 `confirmed` 事实都进入责任人—关闭证据闭环。

## 三条路由

| 路由 | 适用范围 | 规划参考 |
|---|---|---|
| `L-CONTROL` | 中国境内上市公司控制或潜在控制权收购 | [上市控制权路由](references/listed-control.md) |
| `P-EQUITY` | 非上市公司股权收购、控制型增资、分步交易 | [非上市股权路由](references/private-equity-ma.md) |
| `P-ASSET` | 资产、业务或 carve-out 收购 | [资产与业务路由](references/private-asset-ma.md) |

真实混合交易可以叠加路由；每条路由只增加与结构选择直接相关的约束、证据和后续交接事项。

## 固定分析与输出

每次读取 [三维交易结构引擎](references/three-axis-transaction-engine.md)，形成基准、备选、兜底方案；无法形成三条时，逐一列明被排除路径及原因。然后使用 [三维结构方案模板](assets/three-axis-structure-template.md) 和 [输出合同](references/output-contract.md) 生成：

- 同一底层分析派生的管理层决策版与律师执行版；
- 方案编号、关键事实、状态、推荐结论和时间线一致的八部分输出；
- [四类后续任务包模板](assets/downstream-task-packages-template.md)：尽调、交易文件、审批、会计。

四类任务包只定义为验证或落实结构所需的输入、问题、责任人、完成证据和结果回传字段；本 Skill 不执行包内专业工作。

## 法源与专业接口

- 法律依据按 [法源与时效协议](references/legal-authority-protocol.md) 分开现行硬法源、监管或案例观察、历史/草案材料和市场观点。
- 结构化法源索引见 [legal-authorities.json](references/legal-authorities.json)，仅按主题和路由查询；签署、申报、公告、交割或高风险结论前复核官方原文。
- 监管问题只作为路径约束和 [审批任务包接口](references/regulatory-overlays.md)。
- 并表问题只作为证据检验和 [会计任务包接口](references/accounting-control-and-consolidation.md)。
- 文章和历史交易仅作问题种子，见 [article-and-deal-seeds.md](references/article-and-deal-seeds.md)，不得替代现行法源。

## 外国法边界

中国法是当前硬法源范围。境外连接点只识别中国侧 ODI、外汇、国资、经营者集中、数据/技术出口和出口管制接口，并将外国法问题交给当地合资格律师。In v1, do not search for, quote, calculate or state foreign filing thresholds—even with a disclaimer—because no foreign authority/version protocol has been built.

## 明确边界

本 Skill 不负责法律尽职调查或完整尽调，也不完成整套文件起草或审阅、SPA 审阅、全议题谈判、审批申报、会计结论、交割管理、整合或索赔。

交易文件审阅、SPA 审阅和全议题谈判转交后续专业能力；本 Skill 仅输出尽调任务包和交易文件任务包。审批事项只形成审批任务包，不执行申报；会计结论由管理层和会计师出具。交割管理、整合与索赔不属于本产品。

税务、估值、环境、技术、行业和外国法结论由对应专业人士提供。

## 完成状态

- `passed`：六组输入足以确定推荐，三维判断和四任务包闭环；
- `passed_with_limitations`：推荐仍可成立，但存在已披露且不改变当前推荐的假设或外部确认；
- `blocked`：不能启动，或阻断推荐的缺口未关闭。

交付前运行法源与一致性校验；不得用免责声明掩盖事实或专业确认缺口。
