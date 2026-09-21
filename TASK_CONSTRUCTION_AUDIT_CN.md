# §3.1 任务构建与质量验收：证据核对记录

更新：下文记录 9 月 20 日仅核对材料时的状态。9 月 21 日新增的无模型逐任务验收已完成，覆盖 131 个保留任务；新结果与边界见 [验收 V1 报告](output/task_acceptance_v1/README_CN.md)。下表关于尚无逐任务可执行验收的描述是补验前状态，不再代表最新覆盖。

本次修改只核对已有任务、代码和审计产物，补充正文 §3.1 与附录 A；没有新增模型实验、人工标注或评分规则，没有修改原始任务、源表、轨迹及冻结材料。

## 任务来源和集合关系

主实验使用仓库定义的小型合成 CSV 与显式问题、算子配置，不是从真实用户请求中抽样。`toxictool_bench/generate_iclr2027_tasks.py` 保留旧任务，添加广告、库存、诊所、字典和检索证据等数据及问题。

| 任务集 | 实例数 | 规范化规格数 | CSV 数 | 与其他集合的关系 |
| --- | ---: | ---: | ---: | --- |
| `numerical_expanded.jsonl` | 34 | 34 | 11 | 跨模型数值集；全部包含于 60 题扩展集 |
| `semantic_schema.jsonl` | 24 | 24 | 17 | 跨模型语义集；全部包含于 60 题扩展集 |
| `numerical_iclr2027.jsonl` | 60 | 52 | 14 | 34 旧题 + 18 新问题/算子组合 + 8 提示变体 |
| `semantic_schema_iclr2027.jsonl` | 60 | 36 | 22 | 24 旧题 + 12 新问题/算子组合 + 24 提示变体 |
| `realistic_extension_iclr2027.jsonl` | 13 | 13 | 8 | 四组双表，任务 ID 和 CSV 均与前两类分开 |

这里的“规格”直接复用 `analyze_revision_v2.py:template()`：以 dataset、query、poison 配置分组，删除两种固定的检查提示后缀，忽略 severity、poison_probability、poison_once。它不是语义独立性判定；相近问题仍可能属于不同规格。增加 severity 标签也不一定改变实际投毒值。

旧文中的 31/22/56/41/11 个“模板”无法按其所述的 query–dataset–poison 定义从当前文件复现，因此本次改用上述可执行规则，并重算整列；不是删除任务或修改实验统计。若不做规范化，直接对完整 query、dataset、poison 去重，五行分别为 34/24/60/48/13。

补充关系：

- 两个扩展任务集共享 6 个 CSV，合计 30 个不同 CSV；它们的任务 ID 不同。
- 数值参考审计排除 2 个含糊问题，分析集为 58 + 60 = 118；原始发布文件仍为 120 题。
- 分层子集和重复投毒实验复用任务，不应加总成新增任务。
- 最新 200 条人工验证使用扩展集内的 10 个语义任务 ID，以及新增的 10 个数值任务 ID。与评分器开发包按任务 ID 隔离，不宣称模板隔离。
- 24 个结构化真实数据控制任务使用 Palmer Penguins、Auto MPG、Bike Sharing，单独报告，不混入合成主实验矩阵。

## 已有验收证据覆盖什么

| 检查 | 已有依据及覆盖 | 不能据此宣称的内容 |
| --- | --- | --- |
| 正确答案复核 | `toxictool_bench/audit_reference_answers.py`；`toxictool_bench/results/reference_answer_audit.json`。覆盖 60 个扩展数值实例：49 个容差内、7 个数值错误、2 个遗漏并列答案、2 个问题含糊。本次只读重算与存档逐项一致。 | 不能扩展为全部语义、多表参考答案均独立复算通过。 |
| 历史投毒有效性审计 | `toxictool_bench/audit_poison_validity_v3.py`；`output/submission_revision_v3/historical_audit.json`。8 个 adapter 标识，3,319 个记录为投毒的事件，204 个被标记，涉及 157 条轨迹；保留原轨迹进行敏感性分析。 | 未被规则标记不等于已经认证有效；重新标记不能模拟修复后的 agent 行为。 |
| 注入器实现 | `toxictool_bench/tests/test_poisoners.py`。测试完整数字、标签边界、指定字段、错误输出/无变化拒绝、一次投毒状态等。 | 单元用例不是所有任务 × 所有输出形式的语义验收。 |
| 真实数据参考与目标分离 | `toxictool_bench/evidence_controls_v4.py`；`tests/test_evidence_controls_v4.py`。24 题的标准库与 pandas 参考一致，正确值与毒值超出评分容差。 | 不能把这一结构化环境的保证推广到历史自由文本 adapter。 |
| 源数据与恢复路线 | v4 冻结协议记录源文件哈希；环境测试实际执行目标投毒、其他查询及原始行读取，并检查源文件字节不变。历史实现是在工具执行后修改返回值。 | 没有覆盖所有历史合成任务的独立、逐题恢复路径验收日志，也没有历史每次运行前后源文件哈希检查。 |
| 交付记录与人工评分 | v4 完成清单与交付审计覆盖 264 条轨迹；最新人工验证覆盖 200 条轨迹/20 个任务 ID，另有参考勘误复核。 | 人工核对最终答案和行为标签不能替代每一个任务的构建验收。 |

这些边界集中放在附录 A，正文只介绍构建逻辑和关键覆盖。没有把“希望保留恢复路径”写成“全部任务已经执行验证恢复成功”。论文标题、实验结果数值、方法排名和人工结论保持不变。

## 只读复核方法

在仓库根目录运行以下命令，不会生成任务、调用 API 或覆盖审计报告：

```bash
python3 - <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, 'toxictool_bench')
from analyze_revision_v2 import template
from audit_reference_answers import audit

for name in ['numerical_expanded', 'semantic_schema', 'numerical_iclr2027',
             'semantic_schema_iclr2027', 'realistic_extension_iclr2027']:
    path = Path('toxictool_bench/tasks') / (name + '.jsonl')
    tasks = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    sources = {f for t in tasks for f in [t['dataset'], *t.get('aux_datasets', [])]}
    print(name, len(tasks), len({template(t) for t in tasks}), len(sources))

stored = json.loads(Path('toxictool_bench/results/reference_answer_audit.json').read_text())
assert audit() == stored['tasks']
print('Numerical reference audit matches the archived report.')
PY
```

不要为核对而直接运行任务生成器、参考审计脚本的 main 或冻结实验的 freeze：这些入口可能重写材料。本次使用只读函数，不改变冻结输入。
