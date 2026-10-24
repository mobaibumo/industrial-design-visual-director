---
name: industrial-design-visual-director
description: Control industrial product visual consistency during CMF transfer, local edits, scene changes, three-view reference preparation, and visual QA using evidence-based design locks.
---

# Industrial Design Visual Director — V1.1

设计一致性优先于视觉美观。此 Skill 控制已有产品图像编辑，不代替 CAD 几何验证。

## 执行

1. 读取用户请求与可访问设计资料，识别目标图、参考角色和结果图。缺少目标图或设计资料时，仅给最少补充项与任务模板，不编造 DNA。
2. 读取 [Product DNA](references/product-dna.md) 与 [Design Locks](references/design-locks.md)，先实际查看图片再记录观察。保留证据与 Unknown；权威来源冲突必须明示。
3. 按 [Task Routing](references/task-routing.md) 分流；混合任务拆分作用范围。将任务单写为 assets/task-brief.json 的结构。脚本 route 仅提供关键词建议。
   涉及三视图、正/侧/俯视、正交白模上材质或跨视角一致性时，读取 [Three Views](references/three-views.md)。优先使用同一模型导出的视图；单图补视角仅作概念参考。使用 assets/three-view-brief.json 记录视角计划。
4. 按 [Prompt Rules](references/prompt-rules.md) 分配参考角色并生成指令。用 scripts/director.py validate 检查 DNA，用 prepare 生成交付文件。脚本不自动提取图像 DNA。
5. 读取 [Tool Capabilities](references/tool-capabilities.md)，检查当前会话真实工具和授权。可用时按该工具真实接口执行；不可用时交付约束、提示词与人工步骤。prepare 固定记录未编辑，不能当作执行记录。
6. 有实际结果才按 [Visual QA](references/visual-qa.md) 比较图像并记录证据。用 qa 汇总人工/模型填写的 findings；该脚本不识别图像。明确硬锁违规必为 FAIL，遮挡不确定为 REVIEW。
7. 修正时创建新 case/revision 目录，保留原图、旧约束与结果。获得明确授权后才能修订对应硬锁，记录原值、新值、授权原文和 revision。

用户可以只说“做一套三视图”或“给这三张白模统一上材质”。自动组织约束与视图计划，不要求用户手工填写 JSON。普通展示默认正视、右视、俯视并简短说明；准确工程用途缺少模型或可靠投影资料时，询问所需资料，不将概念补全当成工程结果。

## 交付与追踪

默认 outputs/<case-id>/：product-dna.json、design-brief.md、edit-prompt.md、run-manifest.json、change-log.md；仅实际有结果时生成 qa-report.md。输出根目录由用户选择，避免写入 Skill 仓库个人素材。

真实执行后由 Codex 更新 manifest：实际工具名称、调用结果文件、actual_image_edit、execution_status、QA 状态及未验证项。工具失败记录 FAILED；不得仅因存在文件而标记成功。QA 命令输出后同步 manifest 与 change-log。

脚本路径相对此 Skill。Python 3.10+，无必需第三方依赖。使用全路径运行，参数见 `python scripts/director.py --help`。现成示例见 examples；数据格式与边界见 references。原图永不覆盖，私人资料不提交、不上传到非当前任务授权的服务。
