# E3：LLM 多智能体基线与可复现性审计

## 已完成部分

- 构造确定性枚举器，在 0.0063 秒内生成完整的 6,144 个期望配置，不使用 LLM、API 成本为 0。
- 对公开的多智能体产物逐项核对：8,192 次执行只对应 6,144 个唯一配置，重复率 25%；与确定性期望集合相比 precision=1、recall=1。
- 第 1 轮是 -5.5 dBm 的 2,048 个配置；第 2 轮是 -5.5/-5.0/-4.5 dBm 的 6,144 次执行，因此第 1 轮的全部配置在第 2 轮再次执行。

| 方法 | 执行数 | 唯一配置 | 重复率 | 集合精确率/召回率 | 可观测成本 |
|---|---:|---:|---:|---:|---:|
| 确定性枚举器 | 0 次仿真执行 | 6,144 | 0% | 1.0 / 1.0 | 0 API；0.0063 s |
| 公开多智能体产物 | 8,192 | 6,144 | 25% | 1.0 / 1.0 | 未报告 |

## 恢复源码后可确认的实现信息

后来找到的本地工程包含 Planner、Scenario Expander 和 Reflection 三处 LLM 调用及其完整 prompt 模板/JSON 输出约束。作者已确认历史运行使用 OpenAI；恢复的 OpenAI 路径硬编码模型名 `gpt-4o-mini`，system message 为 optical network expert，temperature=0.2，超时默认 90 s，最多尝试 3 次；两轮 refine 控制流至多触发 6 次 LLM 调用。源码快照和哈希保存在 `E5_recovered_gnpy_replay/source/recovered_orchestration_snapshot/`，模板与历史日志的区别见 `E3_llm_baseline/prompt_inventory.md`。

已经保存的是源码中的完整模板，而不是当时每次变量替换完成后的最终请求文本。目录没有 Git 元数据，也没有日期化模型快照、逐调用请求/响应、实际重试次数、token、成本、延迟、失败率或人工干预日志。因此 provider 可明确写为 OpenAI；模型字符串可按恢复源码报告为 `gpt-4o-mini`，但精确模型快照和逐次调用统计仍应标为 `not_reported`，不能根据控制流反推或编造。

## 论文修改建议

在补齐逐调用日志前，把“多智能体显著提高效率/正确性”的强结论降级为案例性描述，并把确定性枚举器列为必需基线。正文可以披露恢复源码的默认模型与参数，但必须与未记录的实际运行元数据区分。8,192 应称为 execution records，而数据集唯一配置数应写为 6,144。原稿若将第一轮功率写为 -5.0 dBm，应改为公开产物实际使用的 -5.5 dBm。

数据表见 `E3_llm_baseline/observable_baseline_comparison.csv` 和 `published_iteration_audit.csv`。
