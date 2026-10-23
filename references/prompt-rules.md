# Prompt Rules
按 Target Image、Reference Images、Edit Objective、Preserve、Allowed Changes、Forbidden Changes、Output Requirements、Uncertainty 顺序写。目标必须明确到文件；每张参考说明仅支配的属性。

“参考图一 CMF 修改图二”：图二为 target，图一为 cmf；禁止迁移图一轮廓、组件、比例。图三为场景时只参考环境。结构指代不明先列待确认，不执行依赖不明确结构的动作。
Preserve 包含所有硬锁与未获授权的条件锁；获得授权的条件锁在该条明确写“本轮允许下列变化”，避免同时要求不变。禁止增加不在授权范围的按钮、轮子、接缝、功能。
局部区域写文字、圈选资产、坐标及坐标系或真实蒙版路径。定位不准列 Uncertainty 并暂停精准局部编辑。输出要求只写实际要求，不虚构分辨率保证。人工步骤应说明打开目标、绑定参考角色、选择区域、输入提示、另存、回传结果审查。
输出后复核允许变化与锁定是否矛盾；脚本仅检查同 target/attribute 的直接冲突，不能替代语义核验。