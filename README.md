# Cross-border M&A Investment Skills

面向投资与并购工作的 Codex Skills 仓库。第一版先把中国法域做深，再以相同的法源版本协议和交易闭环扩展其他法域。

## 已有 Skill

### `handling-china-ma-transactions`

中国投资并购交易工作流，默认买方立场，可显式切换卖方。覆盖：

- A 股上市公司控制权收购；
- 非上市公司股权收购、控制型增资及资产/业务收购；
- 法律尽调、Major Issues、交易结构、SPA/APA 条款、谈判、审批、签约、交割和交割后事项；
- 经营者集中、国资、外资准入、安全审查、ODI/外汇、数据、技术出口和出口管制等中国侧接口；
- 中国买方境外收购的中国侧工作流；外国目标所在地法律由当地合资格律师确认。

它把来源分为现行硬法源、历史/草案、监管与案例材料、市场 playbook 四层。文章和历史交易只用于发现问题，不替代现行法律。结构化法源库保存状态、条款定位、必要短摘、版本关系、官方链接和核验日期，并配有查询与一致性校验脚本。

## 安装

将 Skill 目录复制至个人 Codex skills 目录：

```bash
cp -R skills/handling-china-ma-transactions ~/.codex/skills/
```

在任务中调用：

```text
Use $handling-china-ma-transactions to review this transaction from the buyer perspective.
```

卖方任务请明确写明 `Seller` 或“卖方立场”。

## 验证

进入 Skill 目录后运行：

```bash
python3 -m unittest discover -s scripts/tests -v
python3 scripts/validate_legal_authorities.py
python3 scripts/validate_skill_consistency.py
```

验证器检查数据结构、版本关系、官方域名、路由、模板和文件一致性；它不能替代具体交易中对官方原文、事实材料和专业意见的实时核验。

## 使用边界

- 当前硬法源库核验截至 `2026-08-04`。签署、申报、公告、交割或出具高风险结论时，必须在同一任务再次打开官方原文。
- Skill 是交易分析与工作流工具，不是律师、审计师、税务师、估值师或当地法律顾问的替代品。
- 未公告交易不得把主体名称、价格、结构或文件正文输入外部搜索；应使用抽象法律问题检索。

## 路线图

后续法域将独立维护硬法源、时效状态和当地监管流程，再与中国侧跨境工作流连接。不会在未建立对应法域 reference 前给出外国申报阈值或确定性结论。
