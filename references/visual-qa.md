# Visual QA
比较目标图、锁定档案和结果图，按七维审查：geometry、components、proportions、preserved_cmf、edit_boundary、output_spec、render_quality。记录原图与结果的可见证据、位置/区域、lock_id、严重程度、修正建议及 reviewer。

PASS 需要七维均有可靠支持；缺项 NOT_TESTED；不确定或遮挡 REVIEW；明确硬锁违规 FAIL。汇总优先级 FAIL > REVIEW > NOT_TESTED > PASS。没有可访问结果图一律 NOT_TESTED，不生成空 QA 报告。不同视角必须考虑遮挡、透视、反射，不拿投影差异直接判几何错误。

findings JSON 列表字段：dimension、status、lock_id（可 null）、violation（布尔）、reliable（布尔）、evidence（具体证据）、reviewer、correction。示例见 assets/qa-findings.json。director.py qa 只汇总录入证据，不读取像素判断结构；不得把合成测试证据写成真实观察。
报告须含结果路径、逐项状态与证据、违规锁、修正要求、未验证项。输出规格可用真实图像工具或本地库查尺寸/格式；无此能力记 NOT_TESTED。生成清晰细节不等于真实设计验证；不承诺像素级一致。
修正先处理硬锁，再处理材质与画质；不得自动放宽原约束。

三视图需按 [three-views.md](three-views.md) 逐视角核对对应原图，再检查共享尺寸、方向、组件与 CMF。不得只检查一张就将整套视图标为 PASS；概念补全不构成工程几何验证。
