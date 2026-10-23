# Design Locks
每条包含 id、target、attribute、level、expected、allowed_change、source、confidence、severity。ID 唯一且稳定，source 引用资产 ID。severity 为 critical/major/minor。

Hard 默认锁轮廓、核心体块、连接关系、已确认关键组件数量/位置及用户明确禁止修改项；必须有 Confirmed 或 Observed 证据。Inferred/Unknown 不可升级成设计事实。Hard 的 allowed_change=null；观察证据只锁可观察内容，不锁不可见事实。

Conditional 默认锁 CMF、视角、光照、摆放、背景、画幅，仅当前任务明确授权才可修改。Editable 限于明确授权属性及区域，不能推导整个产品自由编辑。allowed_changes 用 target+attribute 与锁精确匹配，Conditional 必须带 authorization 原文。复杂语义和区域包含关系仍需 Codex 审查。

硬锁与编辑目标冲突时先列出冲突；用户明确授权后新建 revision，记录解除的具体锁、旧值、新值、授权原文。不得为生成方便自行解除。新增两充电口只开放新增项，不解锁杯托。轮眉修改只开放包覆/外露面积，保持轮子数量、棕色、位置与其他结构。

明确硬锁违规 FAIL；遮挡不确定 REVIEW。非硬锁的违反按影响判 FAIL 或 REVIEW，不能因为美观忽略偏差。