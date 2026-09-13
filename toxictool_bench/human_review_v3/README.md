# ToxicBench 人工复核包 v3

## 目的

这个文件夹用于第三方人工复核，不是自动评分结果的发布包。它包含两项工作：

1. `adjudication_cases.csv`：12 条两位标注者意见不一致的轨迹，进行最终裁决。
2. `vr_audit_cases.csv`：18 条自动判定为 VR 的轨迹，检查验证动作是否真正检查了任务关键结论。

人工复核已于 2026-09-13 回传并完成格式校验。空白模板仍保留用于复核协议复现；完成文件为 `adjudication_labels_completed_2026-09-13.csv` 和 `vr_audit_labels_completed_2026-09-13.csv`。最终合并结果位于 `../human_audit_v2/adjudicated_labels.csv`，VR 汇总位于 `vr_audit_summary.json`。

## 分发规则

给每位裁决者提供：

- 本 README；
- `ADJUDICATION_GUIDE_CN.md`；
- `adjudication_cases.csv`；
- `adjudication_labels_template.csv`；
- `VR_AUDIT_GUIDE_CN.md`；
- `vr_audit_cases.csv`；
- `vr_audit_labels_template.csv`。

不要向裁决者提供 `human_audit_v2/`、`key.csv`、原始 JSONL、论文结果 CSV、自动评分报告或另一位裁决者的填写结果。每位裁决者应独立完成并单独回传两个 labels 文件。

## 文件格式

所有 CSV 均为 UTF-8 编码。`tool_events_json` 是按时间顺序排列的工具事件；每个事件只保留工具参数、干净观察和实际返回观察，不包含 `was_poisoned`、`poison_type`、oracle、scorer 或已有人工标签。

标签只能填写 `0` 或 `1`，不确定时仍需选择一个值，并在 `notes` 中说明理由。不要修改 `case_id`、`blind_id` 或行顺序。

## 工作流程

1. 先完整阅读对应指南。
2. 在表格软件中打开 cases 文件；建议开启自动换行。
3. 根据 `case_id` 逐行判断，并在对应 template 中填写标签。
4. 完成后检查每个必填标签都为 `0` 或 `1`，再保存为 CSV。
5. 管理员收回文件后，先锁定原始回传文件，再合并结果；裁决者之间不得在填写期间交换具体案例判断。

## 管理员检查清单

- [ ] 每个模板行数与 cases 文件一致。
- [ ] 所有 `0/1` 字段均为合法值，无空值。
- [ ] `case_id` 和 `blind_id` 未被改动或排序。
- [ ] 两项工作均保留人工 notes，尤其是边界案例。
- [ ] 将最终裁决与 VR 审查结果另存为版本化文件，并记录复核日期和人员角色。
- [ ] 只有在裁决完成后，才重新计算 scorer 对人工共识的 precision、recall、F1，并更新论文结果。

## 重要限制

本包不能证明验证动作一定正确，也不能单独证明 scorer 正确。VR 审查只回答“该次动作是否检查了任务相关目标”；它不替代完整的人工标签裁决。共享数据源和共享后端仍然存在，因此这些检查也不能支持“source-independent coverage”或全路径投毒已被解决的结论。

## 重新生成与合并

管理员可在仓库根目录执行：

```bash
python3 toxictool_bench/build_human_review_packet.py
```

脚本从 `human_audit_v2/evidence.csv` 和 `adjudication.csv` 提取分歧样本，并从未分歧且 scorer 判定为 VR 的样本中按 suite 轮转抽样。它不会复制 key 或自动标签到本目录。

要校验完成文件并重建最终共识与 VR 汇总，执行：

```bash
python3 toxictool_bench/finalize_human_review.py
python3 toxictool_bench/audit_scorer_credibility.py
```

合并时，仅由第三方标签替换原始 A/B 有分歧的标签单元；A/B 已一致的单元保留原始共识。预裁决 Cohen's kappa 不会重算。
