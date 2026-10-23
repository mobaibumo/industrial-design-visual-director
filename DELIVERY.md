# V1.0 交付与验收记录

初始交付日期：2026-10-22。Windows 用户安装目录：`%USERPROFILE%\.codex\skills\industrial-design-visual-director`。

## 文件结构
```
industrial-design-visual-director/
  SKILL.md
  README.md
  LICENSE
  CHANGELOG.md
  DELIVERY.md
  .gitignore
  agents/openai.yaml
  scripts/director.py
  references/
    product-dna.md
    design-locks.md
    task-routing.md
    prompt-rules.md
    visual-qa.md
    tool-capabilities.md
  assets/
    product-dna.json
    task-brief.json
    qa-findings.json
  examples/cmf-transfer/
    product-dna.json
    task-brief.json
    synthetic/A.svg
    synthetic/B.svg
    synthetic/C.svg
  tests/
    cases.json
    test_director.py
    fixtures/invalid-dna.json
```

## 实现边界
|能力|实现|
|---|---|
|Product DNA|由 Codex 查看资料后提取；JSON 模板、证据分类、脚本校验|
|Design Lock|三级约束、硬锁冲突检查、授权变更规则；复杂语义由 Codex 复核|
|Task Router|六模式规则与关键词建议；不承诺独立理解复合/否定请求|
|Prompt Engine|八段结构提示词，多参考角色，保留项与允许修改分离|
|Visual QA|七维证据表和状态汇总，明确硬锁违规 FAIL、遮挡 REVIEW；无自动图像识别|
|Tool Adapter|会话真实工具检查规则、本地能力探测、无工具交付；没有付费 API 集成|
|Revision|目录非空拒绝写入，修订与硬锁授权记录规则|

## 实际执行的自动化验证
- `python -m unittest discover -s tests -v`：14/14 通过，0 失败。
- T01、T06：角色与提示词结构；T02：场景任务保留 CMF；T03：包覆范围与轮子属性；T04：新增端口与保留杯托。
- T05：未知背面与非精确提示；T07：未编辑/NOT_TESTED 与交付完整性；T08：合成证据的 FAIL/REVIEW/NOT_TESTED/PASS 汇总。
- T09：高清化仍保留结构与未验证细节；T10：无目标拒绝生成输出。
- 另测目录/元数据/引用、有效无效数据、硬锁冲突、推测不可硬锁、条件授权与覆盖保护。
- 官方 `skill-creator/scripts/quick_validate.py`：输出 `Skill is valid!`。PyYAML 6.0.3 只装入系统临时目录 `idvd-validation-deps`，Skill 运行仍仅需标准库。
- CLI 冒烟：`outputs/smoke-001` 生成五份文件，未生成 QA 空报告；manifest 为 PROMPT_READY、actual_image_edit=false、qa_status=NOT_TESTED。此目录被 Git 忽略。

上述行为测试使用人工构造输入档案，验证约束处理契约；不证明模型已自主从真实图像正确提取设计。初始交付时，真实图片测试均待执行，没有实际编辑图片，也没有真实视觉 PASS 报告。

2026-10-23 更新：用户报告已完成后续测试，先前还反馈 CMF 迁移时结构保持优于其未使用 Skill 的尝试。未收集逐项测试记录，不能据此标记所有视觉用例 PASS；不将私人测试图纳入仓库。自动化回归测试再次运行，14/14 通过。

## 安装与版本状态
已置于用户 Skill 发现路径并通过官方结构验证；后续已出现在当前可用 Skills 列表中，用户截图展示了明确调用后的实际图像输出。未明确调用时的自动触发稳定性没有受控测试记录。

Git 本地仓库已经初始化并已创建 V1.0 初始提交。初始本地提交使用单次 `Codex <codex@localhost>` 身份，不修改全局配置。现已配置 origin 为 `https://github.com/mobaibumo/industrial-design-visual-director.git`，分支为 main。2026-10-24，经用户明确选择，采用 MIT 许可证，版权署名为 mobaibumo。远程提交与自动化运行结果以 GitHub 实际记录为准。

后续 V1.1 建议：引入更严格的 JSON Schema、真实授权多图回归集、可选尺寸/蒙版校验，以及真实工具执行记录的专用导入命令。
