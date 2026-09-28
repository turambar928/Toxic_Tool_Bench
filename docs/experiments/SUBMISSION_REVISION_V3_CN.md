# 投稿前非人工部分修订记录（V3）

本轮不修改历史轨迹、原始任务、人工标签，也不调整已冻结的答案评分器。
实验结果与旧矩阵分开保存，不能把旧轨迹重新标记后称为“修复投毒器后的实验”。

## 1. 修复投毒有效性

旧 `sign_flip` 翻转返回文本的第一个数字，可能修改 dataframe 行号、日期片段或错误信息，
并消耗 `poison_once`。版本化审计覆盖既有 manifest 中八种 observation-level adapter、
所有算子的 3,319 次已记录投毒事件，发现 204 次 off-target sign-flip，涉及 157 条轨迹。
其中重叠包含：73 次不完整数字 token、20 次数值无变化、6 次错误输出。
这是保守的可机械定位问题清单，不代表其他事件都已通过语义有效性认证。

修复内容：

- sign-flip 只定位配置的 clean value，不再取第一个数字。
- 解析千分位和科学计数法完整数字；拒绝 dataframe 行号、多数字行，以及多个合格标量行上的精确重复匹配。
  这不清除返回中其他格式的正确答案，相关局限见下面的实际结果。
- 可用 `target_field` 进一步约束字段；单个数字匹配本身仍不是字段语义正确性的证明。
- 错误输出、无匹配、数值不变均不计暴露，也不消耗一次机会。
- rank-swap 无匹配时不再用毒答案替换整段输出。
- 冻结 scorer、容差、历史任务和 200 条人工包保持不变。

历史敏感性分析仅改变暴露分类，不改变最终回答，因此 TSR 不变。
另外统一剔除八个 sign-flip 任务后，在剩余 110 个任务上，Double-pass−Base TSR
为 +0.118，任务配对 bootstrap 95% CI [0.064, 0.182]；Guard−Double-pass 为
−0.027 [−0.064, 0.000]。历史方法比较方向保持，但不能据此认证 sign-flip。

## 2. 冻结的新对照

协议：`output/submission_revision_v3/protocol.json`，在取得新答案前固定输入 hash、任务和分析。

- 控制实验：16 个任务 = 全部八个 sign-flip + 三个其他数值任务 + 五个语义任务。
- 模型：`claude-haiku-4-5-20251001`。
- Base：clean/toxic。Double-pass、Verification-only、Guard：各跑 shared 与 per-route。
- shared：两条路线共享一次投毒机会；per-route：每条路线重新获得一次机会。
- 重置的是资格，不是强制投毒，也不保证第二路线全程没有干净观察。
- 每路线最多 10 步，每次模型请求最多 3,072 输出 token，temperature=0。
- 共 128 条轨迹，按任务配对，但不是同一第一路线的分叉重放。
- 报告全任务 TSR、实际暴露、分路线暴露、调用数、工具数、耗时、配对 CI。
- 调用数是逻辑模型调用，不含 HTTP 自动重试；完成轨迹的耗时不含此前放弃的失败尝试，
  调度并发也曾变化，不能把新耗时表当成严格的成本优劣排名。
- 小样本、单模型、单次执行，不能推广为全矩阵排序或估计 API 重复采样不确定性。

另用 CC0 Palmer Penguins 的 344 行真实观测数据，冻结六个聚合/筛选/单位任务，
运行 Base clean/toxic、Double-pass shared/per-route，共 24 条。
来源、许可证、revision 和 hash 随数据发布；标准库与 pandas 两套计算交叉检查参考答案。
这六个任务共享一个公开数据集，可能存在训练集接触，不能当成六个独立领域或生产级验证。

152/152 条轨迹已完成，无缺失或重复条件。共保留八次 HTTP 429 失败尝试，
先降低至四并发，最后对剩余四项串行补跑；已完成轨迹不重跑，只补缺失环境。
执行变更记录在 `rate_limit_recovery.json`、`rate_limit_recovery_2.json`，不按得分重试。

### 实际结果及其边界

| 方法（每个条件 16 个任务） | shared TSR | per-route TSR | 差值 95% CI |
|---|---:|---:|---|
| Double-pass | 16/16 | 15/16 | [−0.1875, 0] |
| Verification-only | 14/16 | 13/16 | [−0.1875, 0] |
| Guard | 16/16 | 13/16 | [−0.375, 0] |

Double-pass 的第二路线暴露从 1/16 增至 12/16，操纵确实改变了投毒条件，
但全部区间包含零。Base 在这个有意覆盖修复问题的子集上已达 16/16，
所以不能说新小样本复现了历史全量 Double-pass 的优势，也不能据此把历史优势
全部归因于后续干净观察。

真实数据四个条件都为 6/6，toxic 暴露分别为 Base 4/6、DP shared 4/6、DP per-route 5/6。
检查发现单次替换常保留另一个正确的四位小数结果：四个有暴露的 Base 返回都是这种情况。
因此这只是“真实表上的部分输出修改与执行检查”，不能作为更强攻击下的恢复或部署鲁棒性证据。
另附 `fresh_residual_reference_inventory.csv`：所有 16 次真实数据投毒事件都含未修改行上的
clean-reference 数值候选；该候选检测本身不认证语义绑定。未根据这些结果修改冻结的规则或挑选重跑。

全量完整性检查、输入/输出 hash、统一重评分及自动生成论文表格已通过。
原有 101 条 VPA 分类在排除历史可疑投毒事件后全部保留；这不等于全部经过人工确认。

## 3. 论文修改

- 摘要、贡献和结果解释聚焦“检查不等于正确采用答案”以及证据条件，不包装成新型强防御。
- 纠正预算单位：3,072 是每次模型请求上限，不是每条路线总 token 上限。
- 历史表明确标注原投毒器；取消根据旧 sign-flip 低 BCR 宣称更鲁棒的解释。
- 新增 delivery 审计及新实验附录；历史敏感性与新采样分开。
- 移除论文中的旧 severity 热图，仓库图文件保留。
- 算子图不再绘制旧 sign-flip 行；原始 CSV 和 Git 历史保留，Figure 1、2 未改。
- 压缩版本修复叙述，详细协议和运行变更保留在附录及 artifact。
- 独立人工评分验证仍待完成，不生成或替换人工结果。

## 4. 复现与检查

```bash
python3 -m pytest toxictool_bench/tests -q
python3 toxictool_bench/audit_poison_validity_v3.py
python3 toxictool_bench/submission_revision_v3.py analyze
python3 toxictool_bench/finalize_submission_v3.py
/home/taozifu2025/.local/bin/tectonic main.tex \
  --outdir output/scorer_revision_v2/pdf --keep-logs
```

新建一份实验才使用 `freeze`；已有协议拒绝覆盖。运行器 `run` 会跳过已有状态记录，
故不能依赖它自动补失败任务。恢复脚本会先检查已有 clean/toxic 行，只运行缺失环境。
不得同时启动多个恢复器；首次调度用到的 reserved 辅助脚本只保留作执行记录，不应重复运行。
`finalize_submission_v3.py` 会检查 152 条预期轨迹无缺失/重复、模型与预算一致、
实际路线及投毒次数合法，并重新计算全部评分；未通过则不生成最终论文表格。

最终检查：134 项测试通过；152 条完整性检查及重评分通过；851 次逻辑模型调用、
577 次工具调用（不包含失败尝试及 HTTP 重试）。PDF 共 30 页，正文在第 9 页结束、
参考文献从第 10 页开始。未发现未解析引用或 overfull 排版；编译器仍有既有的
underfull 和 BibTeX 重跑提示。图与新结果表已检查，API 凭据扫描通过。
原始失败日志的八处行尾空白保持原样，代码及文稿的 whitespace 检查通过。
