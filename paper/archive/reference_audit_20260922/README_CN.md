# 参考文献与引用语境核查（2026-09-22）

## 修订完成状态（同日，审计后经作者确认）

- 已将下表 10 篇条目改为正式会议版本，保留所有引用键，并补入已核实的年份、链接、页码和 DOI。
- SafeRAG 已补 Jihao Zhao、修正作者顺序，并保留正式 PDF 上 Jason Zhaoxin Fan 的完整姓名；RADAR 作者名单未改。
- Related Work 第二段已用 Wu et al. 明确介绍金融代理在污染下验证/检测不一定改善推荐的结果，再说明 ToxicBench 的成对任务、固定源表及检查/采用/恢复指标；同时精确化 Tools Fail 与 PALADIN 的区别。
- TRACE 使用已确认的 ICML 2026 会议归属和官方链接，未填写未经核实的 PMLR 卷页。
- 正文仍为 9 页，全文 27 页；Related Work 保持三段，实际引用仍为 35 篇。静态引用检查通过。
- Overleaf 只需同步 `references.bib` 和 `sections/06_related_work.tex`。未 push。

以下内容保留为修订前的审计记录；其中“当前条目”“建议”指审计时的版本。

## 范围与结论

检查对象为本地 `main.tex` 实际包含的章节、`references.bib` 和编译得到的 `main.bbl`，不是已停止维护的 Overleaf 快照。

- BibTeX 库共 48 条，当前论文实际引用 35 条，13 条未进入参考文献表。
- 静态检查通过：没有缺失引用键、重复文献键或未定义交叉引用。
- 42 条的题名和作者顺序与其链接页面的结构化元数据一致；其余 6 条通过论文 PDF、Crossref、DataCite 或数据集官方推荐引用人工复核。
- 当前 35 篇已引用文献均找到对应来源，没有发现指向完全不同论文、题名杜撰或明显错误的引用键。
- 10 篇已有正式会议版本，但当前仍引用 arXiv 版本。这不等于引用造假或年份填错，建议提交前统一为正式版。
- SafeRAG 的正式版作者表与当前预印本条目不同，切换版本时必须同时处理作者顺序和新增作者。
- 最值得调整的引用语境是 Wu et al. 的金融代理工作：当前表述没有充分体现它与“检查后仍采用错误证据”的直接关联。

初次审计未修改论文或 BibTeX；随后按作者要求完成上述修订，未提交或 push。

## 已有正式版本的 10 篇文献

| 文献 / 当前引用键 | 当前条目 | 已核实的正式版本 | 建议 |
|---|---|---|---|
| ToolLLM / `qin2023toolllm` | arXiv 2023 | [ICLR 2024](https://iclr.cc/virtual/2024/poster/18267) | 换正式会议条目，显示年份改为 2024 |
| API-Bank / `li2023apibank` | arXiv 2023 | [EMNLP 2023](https://aclanthology.org/2023.emnlp-main.187/)，3102–3116，DOI 10.18653/v1/2023.emnlp-main.187 | 年份不变，补正式会议、页码和 DOI |
| AgentBench / `liu2023agentbench` | arXiv 2023 | [ICLR 2024](https://iclr.cc/virtual/2024/poster/17388) | 换正式会议条目，显示年份改为 2024 |
| WebArena / `zhou2023webarena` | arXiv 2023 | [ICLR 2024](https://iclr.cc/virtual/2024/poster/17826) | 换正式会议条目，显示年份改为 2024 |
| SafeRAG / `liang2025saferag` | arXiv 2025 | [ACL 2025](https://aclanthology.org/2025.acl-long.230/)，4609–4631，DOI 10.18653/v1/2025.acl-long.230 | 换正式版，同时核对作者，见下文 |
| MICE / `subramani2025mice` | arXiv 2025 | [NAACL 2025](https://aclanthology.org/2025.naacl-long.615/)，12362–12375，DOI 10.18653/v1/2025.naacl-long.615 | 年份不变，补正式会议、页码和 DOI |
| RADAR / `gu2025radar` | arXiv 2025 | [NeurIPS 2025 Datasets and Benchmarks](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a0434f04b6437e875d52d0b0e25c1729-Abstract-Datasets_and_Benchmarks_Track.html)，卷 38，DOI 10.52202/085713-3699 | 换正式版；作者应以正式 PDF 为准，不要直接照抄网页元数据 |
| MetaRAG / `zhou2024metarag` | arXiv 2024 | [The ACM Web Conference 2024](https://doi.org/10.1145/3589334.3645481)，1453–1463 | 年份不变，补正式会议、页码和 DOI |
| PoisonedRAG / `zou2024poisonedrag` | arXiv 2024 | [USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/zou)，3827–3844 | 换正式会议条目，显示年份改为 2025 |
| TRACE / `kim2025trace` | arXiv 2025，链接 v3 | [ICML 2026](https://icml.cc/virtual/2026/poster/64255) | 正式会议已由官网确认，显示年份可改为 2026；不要猜测尚未核实的 PMLR 卷页 |

年份应与实际引用的版本配套。保留预印本时，2023/2024/2025 这些原始年份本身并不错误。若改为正式版，可以保留现有 BibTeX key，修改 `year`、条目类型和发表信息即可，不必全局重命名引用键。

### SafeRAG：不能只修改会议名称

当前 `references.bib` 与所链接 arXiv 页面一致，但 [ACL 正式 PDF 首页](https://aclanthology.org/2025.acl-long.230.pdf) 的作者顺序为：

Xun Liang → Simin Niu → Zhiyu Li → Sensen Zhang → Hanyu Wang → Feiyu Xiong → Jason Zhaoxin Fan → Bo Tang → **Jihao Zhao** → **Jiawei Yang** → Shichao Song → Mengwei Wang。

相对当前条目，正式版新增 Jihao Zhao，并把 Jiawei Yang 放在 Shichao Song、Mengwei Wang 前面。ACL 网页 BibTeX 将 Jason Zhaoxin Fan 简写为 Zhaoxin Fan，而 PDF 使用全名；当前全名并不是错误。

### RADAR：不要被网页作者元数据误导

NeurIPS 网页元数据和会议个人主页展示的作者名单遗漏 Girish Narayanswamy，并使用 Max Xu、Xuhai “Orson” Xu 等姓名形式。但 [NeurIPS 正式 PDF 首页](https://proceedings.neurips.cc/paper_files/paper/2025/file/a0434f04b6437e875d52d0b0e25c1729-Paper-Datasets_and_Benchmarks_Track.pdf) 明确包含 Girish Narayanswamy，并使用 Maxwell A Xu、Xuhai Xu，和当前条目一致。此处不应机械删改作者。网页的 publication date 为 2026-04-23，但论文首页明确为 NeurIPS 2025，不能仅凭网页上传日期把会议年份改成 2026。

## 正文引用是否支持对应论述

### 可以保留的核心引用

| 当前引用位置 / 论述 | 原文依据与判断 |
|---|---|
| Introduction：工具辅助计算与交互，引用 ReAct、Toolformer、PAL | 支持。PAL 把求解交给程序解释器；ReAct 联合推理与外部交互；Toolformer 学习 API 调用。 |
| Introduction / Related Work：数据工程、分析任务，引用 DAComp | 支持。DAComp 明确划分 repository-level 数据工程和开放式分析。 |
| Introduction：从最终结果转向轨迹和错误传播，引用 AgentAtlas、AgentProp-Bench | 支持这一一般性定位。没有把 AgentAtlas 的协议示例夸大为真实生产数据，也没有复述 AgentProp-Bench 的具体估计数值。 |
| Introduction / Related Work：Tools Fail 的 silent errors | 支持。官方摘要直接提出 silent tool errors 及 calculator / embodied planning recovery。 |
| ToolBench-X 的 recoverable hazards | 支持。原文列出五类危害并保留 retry、fallback、verification 等恢复路径。 |
| ToolRobustBench：stage-aligned perturbations、deterministic / cascade-aware diagnosis、单次调用内诊断 | 支持。[原文](https://arxiv.org/html/2608.23635v1) 明确写出 “within a single tool-calling episode, not a multi-turn recovery benchmark”。当前没有错误宣称它只评最终答案。 |
| TRACE：evidence bank 和 LLM-based trajectory evaluation，三个维度 efficiency / hallucination / adaptivity | 支持。[§3.2 及 Figure 2](https://arxiv.org/html/2510.02837v3) 直接描述 evidence bank 与三类评价；当前区别是观察证据支持与源数据正确性，不是宣称 TRACE 实验失败。 |
| RADAR 与源数据质量问题的区别 | 支持。RADAR 对表格引入缺失值、异常、逻辑不一致等数据问题；ToxicBench 的返回观察干预不同。 |
| Greshake et al.、AgentDojo：间接提示注入 | 支持。研究恶意指令通过外部内容/工具数据进入上下文，与纯事实/语义观察腐败有区别。 |
| MCP-ITP、TRUSTDESC：tool metadata / descriptions | 支持。前者在工具元数据中嵌入指令，后者从实现生成可信描述。 |
| PoisonedRAG、SafeRAG：retrieved content | 支持。当前 Related Work 用的是宽泛的 retrieved content，不是把 SafeRAG 全部攻击错误描述为数据库写入。 |
| Reflexion、Self-Refine、MetaRAG、ToolCritic：反馈、自监控与修订 | 支持。ToolCritic 的修订也覆盖工具调用和工具输出解释，不限于最终文字答案。 |
| Confidence Dichotomy 与 MICE：校准及工具决策 | 一般性表述可保留。MICE 明确使用估计置信度决定是否调用工具；Confidence Dichotomy 更侧重不同工具对校准的影响。若细化，宜分别描述。 |
| §4.4：DAComp 区分 scoring agreement 与 comparison stability | 支持。[DAComp 的验证章节](https://arxiv.org/html/2512.04324v1) 分别使用 item agreement、task-level ICC(A,1)、model-level Kendall’s tau-b。当前只是借鉴评价维度，没有声称采用完全相同的指标。 |
| 附录公共数据来源 | Palmer Penguins、Auto MPG 和 Bike Sharing 的作者、年份与官方推荐引用/DataCite 一致。数据集引用不是同名方法论文。 |

### 应加强：Wu et al. 的金融代理工作

位置：`sections/06_related_work.tex` 第二段，目前仅将其归为 “financial tool data”，对应 `wu2026agentdrift`。

[《Sell Me This Stock: Unsafe Recommendation Drift in LLM Agents》v8](https://arxiv.org/html/2603.12564v8) 不仅研究金融数据篡改，还在 §5.3 和 Appendix Y 讨论：

- self-verification 因重新依赖被操纵的工具数据而失效；
- parametric cross-check 能标记污染，但最终推荐仍未相应改善。

这与本文“检查/识别不等于改变最终采用答案”的现象相近。当前引用对象没有错，但定位过于简略，容易显得没有充分承认已有认识。建议用一到两句明确共同点，再说明本文的任务、干预和测量区别，不宜暗示该现象首次出现。

可参考的替换表达（尚未写入正文）：

> Wu et al. study financial recommendation drift under manipulated tool data and find that self-verification or contamination detection need not change recommendations. ToxicBench examines related evidence-use failures through paired data-analysis tasks, fixed source tables, and separate checking, adoption, and recovery metrics.

“AgentDrift” 不是论文正式题名；本次所读全文主要在软件包名中使用该词。直接写 `\citet{wu2026agentdrift}` 或 financial recommendation drift 更容易检索与定位。版本历史里 v5 曾 withdrawn，但后续有 v6–v8，本次引用和判断基于可访问的 v8，不能把一个历史版本撤回直接当作整篇论文无效。

### 可选的小幅精确化：PALADIN

Related Work 将 Tools Fail、ToolBench-X、PALADIN 放在 “Silent errors and recovery” 同一句，并非明显错引，但容易让读者以为三者都专门研究 silent errors。PALADIN 摘要主要列 timeout、API exception、inconsistent outputs 等广义工具故障。更精确的表达可将 Tools Fail 的 silent errors 与另外两篇的 tool failures / recovery 分开。无需增加新段落。

## 其余已引用条目的来源检查

以下 25 条不属于上面的正式版本更新清单；本轮没有发现其当前元数据与所引用来源的实质冲突。

| 引用键 | 核验来源 / 说明 |
|---|---|
| `yao2023react` | [arXiv](https://arxiv.org/abs/2210.03629) 注明 ICLR camera-ready；引用 ICLR 2023 正确，不应改成首次预印本的 2022 |
| `schick2023toolformer` | [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html)，包括 Eric Hambro 的作者列表一致 |
| `patil2024gorilla` | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/e4c61f578ff07830f5c37378dd3ecb0d-Abstract-Conference.html) |
| `gao2023pal` | [ICML 2023 / PMLR 202](https://proceedings.mlr.press/v202/gao23f.html)，10764–10799 |
| `greshake2023indirect` | [Crossref DOI 元数据](https://api.crossref.org/works/10.1145/3605764.3623985)，AISec 2023 workshop、79–90；不是 CCS 主会 |
| `breck2019data` | [MLSys 2019 PDF](https://proceedings.mlsys.org/paper_files/paper/2019/file/928f1160e52192e3e0017fb63ab65391-Paper.pdf) 首页：Breck、Polyzotis、Roy、Whang、Zinkevich，当前顺序正确 |
| `schelter2018automating` | [PVLDB 2018 PDF](https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf)，11(12):1781–1794 |
| `shinn2023reflexion` | [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)，当前正式作者列表正确 |
| `madaan2023selfrefine` | [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html) |
| `xuan2026confidence` | [arXiv:2601.07264](https://arxiv.org/abs/2601.07264) |
| `li2026mcpitp` | [arXiv:2601.07395](https://arxiv.org/abs/2601.07395) |
| `ye2026trustdesc` | [arXiv:2604.07536](https://arxiv.org/abs/2604.07536) |
| `vuddanti2025paladin` | [arXiv:2509.25238](https://arxiv.org/abs/2509.25238) |
| `mazaheri2026agentatlas` | [arXiv:2605.20530](https://arxiv.org/abs/2605.20530) |
| `wu2026agentdrift` | [arXiv:2603.12564](https://arxiv.org/abs/2603.12564)，元数据正确，语境建议见上 |
| `gurram2026agentprop` | [arXiv:2604.16706](https://arxiv.org/abs/2604.16706)，题名为 Auditing Automated Evaluation, Error Propagation, and Runtime Mitigation in Tool-Using Language Agents |
| `hamad2025toolcritic` | [arXiv:2510.17052](https://arxiv.org/abs/2510.17052) |
| `sun2024toolsfail` | [EMNLP 2024](https://aclanthology.org/2024.emnlp-main.790/)，14272–14289 |
| `debenedetti2024agentdojo` | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html) |
| `tian2026toolbenchx` | [arXiv:2606.25819](https://arxiv.org/abs/2606.25819) |
| `zheng2026toolrobustbench` | [arXiv:2608.23635v1](https://arxiv.org/abs/2608.23635v1) |
| `lei2025dacomp` | [arXiv:2512.04324v1](https://arxiv.org/abs/2512.04324v1) |
| `horst2020palmerpenguins` | [官方 Citation](https://allisonhorst.github.io/palmerpenguins/authors.html)，Horst/Hill/Gorman 2020；当前未写包版本不构成错引 |
| `quinlan1993autompg` | [DataCite](https://api.datacite.org/dois/10.24432/C5859H)，R. Quinlan，1993 |
| `fanaee2013bikedata` | [DataCite](https://api.datacite.org/dois/10.24432/C5W894)，Hadi Fanaee-T，2013 |

对上述仍为 arXiv 的条目，“来源一致”不代表已经穷尽证明其绝无其他发表版本，也不代表为其研究质量背书。

## 13 条未使用的 BibTeX 条目

`perez2022ignore`、`chen2025poisonarena`、`li2025cparag`、`dekel2026sdag`、`li2026agentcanary`、`vuddanti2026err`、`jia2025ragrank`、`wang2026mirror`、`kohl2026structural`、`zhang2026agentsentry`、`zhang2025cosight`、`ma2025pou`、`patil2026ragshield`。

这些条目的题名和作者也与其 arXiv 链接元数据匹配，但未进入当前 PDF 的 References，不是缺失引用或编译错误。无需为了“凑引用”重新插入正文。

## 实施顺序建议

1. 统一上述 10 篇的发表版本；SafeRAG 同步作者，RADAR 保留 PDF 上的完整作者。
2. 补强 Wu et al. 的直接相关定位；可同时精确化 PALADIN 那一句。
3. 保留目前对 TRACE、ToolRobustBench、DAComp 的主要描述，不需要重写。
4. 重新编译检查正文页数、作者—年份标签和引用链接。保持现有 citation key 可以降低遗漏风险。

在线页面不全部可直接访问：ACM 页面触发反爬后用出版商提交的 Crossref 元数据核验；OpenReview 页面/PDF 触发验证后改用 ICLR/ICML 官方会议页、NeurIPS proceedings 和原文 arXiv HTML。TRACE 的正式会议归属已确认，但本轮未核实 PMLR 卷号和页码，不应补造。
