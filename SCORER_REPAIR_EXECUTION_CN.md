# 评分器修复、重评分与论文修订执行报告

更新时间：2026-09-16

## 结论

计划中的离线修复已经完成：冻结新版答案选择器、审计数值参考答案、对 5,396 条历史轨迹做三版本重评分、刷新论文表格和图、加入任务依赖敏感性分析，并将正文压到 ICLR 初投要求的 9 页以内。原始轨迹、原始任务和人工标签没有被覆盖。

冻结后的 110 条新模型轨迹已经全部完成。绕过服务器本地代理后，Claude Haiku 的 50 个作业、90 条 core/repeated 轨迹全部成功且零失败。原指定的 GPT-5.4-mini 没有可用路由；第一次获批替换的 GPT-5.6-sol 能普通对话但 function tools 返回 404，因此没有产生完整 cross-model 轨迹。所有 cross-model 答案产生前又记录了第二份用户授权 amendment，改用通过 tool-call 预检的 Claude Sonnet 4.6，随后 10 个 AutoGen 作业、20 条轨迹全部成功。当前盲审包为 200/200，但双人人工标注尚未开始，所以模型执行完成仍不等于独立验证完成。

## 已完成的修复

1. 新答案选择器先定位回答的结论/更正片段，再与 oracle 比较。它支持千位分隔符、百分号、科学计数法、带符号数、实体—数值绑定、明确改口和并列 clean aliases。实现冻结在提交 `98c2ed8`。
2. 已增加 19 个答案解析回归测试，并保留旧运行时代码依赖的兼容函数。
3. 独立地用 dataframe 运算复算了 60 个 expanded numerical 任务，而不是从原 oracle 反推。
4. 所有论文相关实验统一使用评分视图中的修订参考答案；原 JSONL 和历史毒化目标不变。
5. PandasAI 的历史 adapter 是在 `agent.chat` 完成后修改最终字符串，agent 没有观察或采用该证据。它已从正文行为比较、跨模型均值和 operator profile 中移除，原始结果保留在归档中。

## 参考答案审计

审计发现：

- 7 个数值实例超出原任务容差，包括 3 个 repeat 实例；
- 2 个实例漏收并列最优答案 A100/B200；
- 2 个 channel-ranking 实例没有说明 conversion rate 的分母，按 clicks 或 impressions 会得到不同赢家。

前两类通过只读 scoring overlay 修正；两道歧义题从所有修订后方法比较中排除。最终主分析为 118 个单表任务、944 条 defense 轨迹和 1,572 条 repeated-poison 轨迹。历史人工包中有 40 条受参考答案变化影响，已单独生成复核包；旧标签未被改写。

## 重评分结果

在曾用于发现问题的 240 条历史审计轨迹上，新评分器与原共识标签的 TSR 一致率为 238/240（99.2%），precision 为 1.000，recall 为 0.990。PAR 7/7、BCR 3/3、VPA 4/4 均被识别；RR recall 为 0.972，VR recall 为 0.988。由于这些数据参与过修复，这些数字是 development recheck，不是独立准确率；BCR/VPA 阳性数太少，也不能证明广泛召回率。

修订后的 118-task defense 结果为：

| 方法 | Clean TSR | Poisoned TSR | BCR | VR | RR |
|---|---:|---:|---:|---:|---:|
| Base | 0.99 | 0.89 | 0.09 | 0.46 | 0.44 |
| Double-pass | 0.99 | 1.00 | 0.00 | 0.98 | 0.98 |
| Verification-only | 0.92 | 0.90 | 0.00 | 0.97 | 0.86 |
| Generic Guard | 0.98 | 0.97 | 0.00 | 0.97 | 0.94 |

Double-pass 相对 Base 的 poisoned TSR 差为 +0.110；按 87 个模板 cluster 重采样的 95% CI 为 [0.056, 0.171]，按 30 个 dataset cluster 重采样为 [0.060, 0.172]。Guard 相对 Double-pass 为 -0.025，两个区间上界均为 0，因此论文不再主张 Guard 优于 Double-pass。

Repeated-poison 中有 101 条修订后 VPA 轨迹：78 条的所有合格后续检查均被污染；23 条至少有一个未修改检查，但仅 1 条自动匹配 clean reference，且其证据充分性仍待人工判断。论文因此只声称“检查后仍采用错误答案”，不声称 101 条都忽略了充分且正确的证据。

## 独立验证协议与当前阻塞

冻结协议包含 20 个 task ID 和 200 条轨迹：90 条未参与 parser 开发的既有 semantic 轨迹，以及 110 条冻结后新 numerical 轨迹。10 个新 numerical task 已由标准库和 pandas 两套实现交叉核对，runner 支持按 source hash 断点续跑。

当前状态：

- 模型轨迹：200/200；其中 90 条复用 semantic、90 条新 Haiku numerical、20 条新 Sonnet--AutoGen numerical；
- 有效新运行：60 个作业、110 条轨迹，全部完成；另有 1 次 GPT-5.6 tool-call 不兼容尝试被 manifest 排除；
- 人工标注：未开始；
- API：绕过本地代理；两个 model amendment 均在 cross-model 答案产生前记录；
- reviewer packet：200/200，完整但仍是空白人工标注表；
- 40 条参考勘误：单独复核，不混入独立验证。

模型轨迹已经完成；若只需验证包完整性，可重新执行：

```bash
python3 toxictool_bench/build_validation_v2_packet.py
```

完成 200 条后，将 `reviewer_packet.zip` 分别交给两名标注者；冻结规则期间不得根据验证结果继续调 parser。第三人只裁决分歧，同时保留 A/B 原始表。

## 复现与验收

核心离线命令：

```bash
python3 toxictool_bench/audit_reference_answers.py
python3 toxictool_bench/sync_primary_paper.py
python3 toxictool_bench/sync_defense_paper.py
python3 toxictool_bench/summarize_verification_stress.py
python3 toxictool_bench/sync_supplementary_paper.py
python3 toxictool_bench/analyze_revision_v2.py
python3 -m pytest toxictool_bench/tests -q
python3 toxictool_bench/check_paper_static.py
tectonic main.tex --outdir output/scorer_revision_v2/pdf --keep-logs
```

验收结果：116 项测试通过；论文正文在第 9 页结束，参考文献从第 10 页开始；生成的版本化分析 manifest 保存输入 SHA-256。关键文件为：

- `output/scorer_revision_v2/analysis_manifest.json`
- `output/scorer_revision_v2/trajectory_changes.csv`
- `output/scorer_revision_v2/cluster_sensitivity.csv`
- `output/scorer_revision_v2/development_recheck/`
- `output/scorer_revision_v2/final_validation/protocol.json`
- `output/scorer_revision_v2/final_validation/protocol_amendment_gpt56.json`
- `output/scorer_revision_v2/final_validation/protocol_amendment_sonnet46.json`
- `output/scorer_revision_v2/final_validation/new_run_manifest.json`
- `output/scorer_revision_v2/final_validation/reference_errata_review.zip`
- `output/scorer_revision_v2/final_validation/reviewer_packet.zip`（200/200，待人工标注）

## 投稿前必须补完

1. 两名人工独立完成 200 条 validation 标注，第三人裁决分歧。
2. 单独复核 40 条 reference errata；若标签变化，重新同步论文数字。
3. 只在上述人工结果完成后，将“pending independent validation”替换为真实结果；不能把 development recheck 或仅完成模型调用写成独立验证。
