# Industrial Design Visual Director V1.1

为已有工业产品的 AI 图像编辑建立可追溯约束。支持产品 DNA、三级设计锁、CMF 迁移、局部修改、背景替换、渲染优化、多视角分析与 Visual QA。首版不从单图恢复准确 CAD；Python 脚本不做图像识别或图像生成。

## 安装与调用
项目地址：[mobaibumo/industrial-design-visual-director](https://github.com/mobaibumo/industrial-design-visual-director)。

Windows 已安装 Git 时，在 PowerShell 执行（目标目录必须不存在；已有安装请勿覆盖）：
```powershell
git clone https://github.com/mobaibumo/industrial-design-visual-director.git "$env:USERPROFILE\.codex\skills\industrial-design-visual-director"
```

也可以点击 GitHub 的 **Code → Download ZIP**，解压后将目录重命名为 `industrial-design-visual-director` 并放入下面的安装路径。ZIP 安装不会自动更新；Git 安装可在确认无本地改动后运行 `git pull --ff-only` 更新。

将整个 Skill 目录放在 `%USERPROFILE%\.codex\skills\industrial-design-visual-director`，不要只复制 SKILL.md。打开新 Codex 聊天后输入 `$industrial-design-visual-director`；若列表未刷新，重启应用。

独立仓库可以直接克隆到上述安装目录，让 Git 工作目录与安装目录保持一致。若存放在综合 Skills 仓库中，需将完整子目录安装到该路径，并明确记录更新/同步方式。用户项目中的输出应放在项目自己的 outputs 下。

可复制：
```
使用 $industrial-design-visual-director，把图二产品的 CMF 换成图一的风格。
```

## 用一句话修改产品
无需写出复杂约束。Skill 应根据目标产品与修改范围建立设计锁。同一聊天继续修改时，可以直接说“只把耳垫改成棕色”或“橙色少一点，其他保持”。新任务建议明确调用一次，便于确认测试使用了本 Skill。资料不足、局部位置不明时仍可能需要补充信息。

## 三视图：一句话调用

上传一张产品图，可以说：
```
使用 $industrial-design-visual-director，做一套产品三视图，造型和材质保持一致。
```
默认正视、右视、俯视；单图缺少的信息会标为未知，生成结果仅为概念参考，不能直接当作准确工程图。

上传同一模型导出的三张正交白模图和 CMF 参考图，可以说：
```
给这三张白模统一上参考图的材质，保留各自视角、轮廓和结构，背景用浅灰色。
```
Skill 会按视图绑定原图，统一组件材质，并检查高度、宽度、深度的对应关系及镜像、遮挡和结构漂移。真实模型导出需当前环境有相应工具；AI 上材质后的结果仍需审查，不自动继承 CAD 精度。详细规则见 [三视图说明](references/three-views.md)。

三视图任务单可参考 `assets/three-view-brief.json`，与示例 DNA 搭配运行 prepare；它只准备指令，不自动生成或验证图片。

## 运行脚本与自动化测试
脚本为可选辅助工具，日常用自然语言调用 Skill 即可。需要 Python 3.10+，运行脚本无需第三方依赖。在 PowerShell 中执行（若系统命令是 `python`，将 `py -3` 替换为 `python`）：
```powershell
Set-Location "$env:USERPROFILE\.codex\skills\industrial-design-visual-director"
py -3 -m unittest discover -s tests -v
py -3 scripts/director.py validate examples/cmf-transfer/product-dna.json
py -3 scripts/director.py prepare --dna examples/cmf-transfer/product-dna.json --brief examples/cmf-transfer/task-brief.json --out outputs/demo-001
py -3 scripts/director.py capabilities
```
prepare 不编辑图片，输出 manifest 明确记录 NOT_TESTED。再次运行请换新输出目录。示例路径相对 examples/cmf-transfer；真正处理图片前应解析为可访问绝对路径。示例 SVG 均为项目自制合成素材，四轮数量属于合成设计说明，不代表隐藏结构推断。

先复制 assets 的 JSON 模板，替换产品特征、证据和参考路径；请 Codex 实际查看素材后填写，避免把示例产品当成你的设计。字段规范见 references/product-dna.md。修改后的 DNA 用 validate 检查。任务单中的 allowed_changes 逐项写 target、attribute、value、authorization。

实际结果出来后，请 Codex 按 references/visual-qa.md 对照原图填写 findings JSON，然后执行：
```powershell
py -3 scripts/director.py qa --dna outputs/demo-001/product-dna.json --result 'D:\project\result.png' --findings 'D:\project\findings.json' --out outputs/demo-001/qa-report.md
```
该命令汇总证据，不自动观察图片；审查后同步 manifest 与修改记录。没有结果时不创建空 QA 报告。完整能力与测试记录见 DELIVERY.md。

## Git 与隐私
本项目采用 [MIT 许可证](LICENSE)，允许使用、修改、分发和商用，须保留版权声明及许可声明。软件按原样提供，不作担保。

提交前检查 `git status`、`git diff --cached`，私人图片、CAD、密钥和 outputs 不入库。`.gitignore` 不是完整的隐私检测器。用户输入的私人设计素材不因使用本 Skill 而成为本项目的开源内容。

## 测试范围
21 项自动化测试覆盖数据格式、设计锁、三视图计划与输出状态等行为契约，不代表真实图像编辑质量。三视图新增测试使用合成声明，没有执行真实 CAD 导出或三视图生成。维护者另报告已完成原版实际使用测试，并观察到 CMF 迁移时的结构保持优于其未使用 Skill 的尝试；该反馈没有作为受控对比实验或量化保证。私人测试图片不随仓库分发。

## 后续改进
可扩展 JSON Schema、否定/复合意图的语义评测、可选的蒙版边界与输出尺寸检查，以及真实多图回归样本。新增适配器须按可用工具接口实现，不假设付费 API。
