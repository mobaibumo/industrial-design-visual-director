# Tool Capabilities
先检查本轮会话工具列表与真实接口，分别记录：图像读取/分析、编辑/生成、本地图片处理、文件/测试。`director.py capabilities` 仅检测本地 Python 能力，CHECK_SESSION 不是可用或已授权。

用图像查看工具实际检查输入。具备图像编辑工具且当前请求授权时，读取其说明/必要 Skill，按真实参数调用；不要编造 API、环境变量、密钥或服务。引用所有必要目标图；工具无法访问素材时请补图或修复路径。当前任务授权不扩展到公开上传私人图像。

无编辑工具仍完成 DNA、任务单、提示词、人工操作步骤、manifest 和 change-log；actual_image_edit=false、execution_status=PROMPT_READY、qa_status=NOT_TESTED，等待结果。失败记 FAILED 和实际错误，不假装成功；不无限重试，重复失败则保留交付供人工执行。

真实编辑成功才记工具名、结果路径与调用证据；存在结果后再视觉审查。V1 无付费服务依赖。原图只读，生成新文件；目录非空时换新 revision，不静默覆盖。