# PE/VC 融资审阅交接包

事项：  
路由：OUT-PEVC（来源筛查可为 L-CONTROL / P-EQUITY / P-ASSET）  
立场：Buyer（默认） / Seller / Investor / Company / Founder  
As-of / 法律核验日：  
材料范围 / 版本：  
关键假设：  
法域：中华人民共和国境内 / Offshore USD / VIE（待目标 Skill 确认）  
完成状态：passed / passed_with_limitations / blocked

## 转交目标

调用：`$pe-vc-transaction-docs-review`

本交接包只传递已确认的路由事实和边界判断，不替代目标 Skill 的文件预检、法律核验或完成闸门。

## 三维状态

| 维度 | 状态 | 已确认事实 | 风险触发器 |
|---|---|---|---|
| 控制权 | not-sought / pending-professional-confirmation |  |  |
| 收购方式 | not-applicable；事项实质为新增融资 |  |  |
| 合并财务报表 | not-sought / pending-professional-confirmation |  |  |

## 转交理由

- [ ] 未上市公司纯新增股权融资；
- [ ] 不以取得现有股权、业务或资产为目的；
- [ ] 不属于分步取得控制或其他并购组合的一部分；
- [ ] 用户需要融资文件、投资人权利、市场惯例或多轮红线审阅。

若任一项不能确认，先留在 `$handling-china-ma-transactions` 完成并购实质和交易路由判断。

## 控制风险触发器

发现下列事项时，目标 Skill 应回调本 Skill 重新判断 `P-EQUITY`、经营者集中控制及并表影响：

- 投资人可决定或共同决定预算、商业计划、融资、重大合同或关键管理层；
- 投资人出席构成董事会或股东会处理普遍事项的法定人数条件；
- 保护性事项超出基础权利保护，形成对相关活动的实质性否决；
- 本轮包含老股受让、业务/资产收购，或是后续取得控制的前置步骤；
- 文件安排与用户“不寻求控制或并表”的描述不一致。

## 文件与版本

| 文件 | 版本/日期 | Clean / Redline / Track Changes | 可读状态 | 上一版/基线 | 备注 |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

常见文件：term sheet、增资/认购协议、股东协议、章程、披露函、side letter、ESOP、VIE 文件及交割文件。

## 审阅立场

- 用户角色 / 审阅目的：
- 代表方：Investor / Lead / Follow-on / Strategic / Company / Founder：
- 架构：RMB onshore / Offshore USD direct / Offshore USD VIE：
- 适用法律 / 争议解决：
- 当前轮次及版本基线：
- 保密级别 / 是否允许跨事项比较：

## 期望交付

- 审阅范围：全文 / Track Changes / 版本比较 / 单条款；
- 输出模式：问题清单 / 批注 / Major Issue List / 红线稿（须用户明确要求）；
- 输出语言：
- 重点条款与用户底线：
- 仍缺的必要信息或文件：

## 交接边界

- 并购 Skill 不替目标 Skill 判断市场惯例、生成融资条款或追踪多轮谈判；
- 目标 Skill 不以“保护性权利”标签替代控制实质分析；
- 如控制风险触发器被命中，两个 Skill 按“融资文件审阅继续、控制与并购结构回调”的方式并行分工。
