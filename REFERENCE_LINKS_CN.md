# 参考文献逐条人工核查清单

整理日期：2026-09-24。来源：[references.bib](references.bib)。

本清单严格按照 Bib 文件中条目的出现顺序排列，不是 PDF 参考文献的作者字母顺序。共 48 条：45 条论文类条目、3 条数据集或软件资源；当前主论文及附录引用了其中 35 条，另有 13 条保留在 Bib 中但未引用。引用状态按当前主文件及其实际载入的 TeX 内容统计。

优先提供已确认的正式会议、论文集或出版方的论文详情页，而非 PDF 直链，便于查看摘要、出版信息和 BibTeX。未确认正式出版页面的条目保留 arXiv 摘要页；这不意味着断言该论文从未发表。会议官网的 poster 页面也可能是主会录用论文的官方入口，与独立的 poster-only 项目不同。DOI 链接可能跳转到需要机构访问权限的出版平台。

勾选框留给你逐条核查：链接对应的标题、作者、年份及发表场所是否匹配；然后对照论文原文，判断我们引用它的那句话是否得到支持。**有正确链接不等于引用论断已经核查正确。** 本次只整理清单，没有修改 Bib 或论文正文。

## 按 Bib 原始顺序核查

- [ ] 01. ReAct: Synergizing Reasoning and Acting in Language Models

  引用键：`yao2023react`；状态：已引用；Bib 年份：2023。

  优先阅读：[ICLR 2023（官方会议页面）](https://iclr.cc/virtual/2023/poster/11003)。

  预印本对照：[arXiv](https://arxiv.org/abs/2210.03629)。

  核查提示：Bib 当前链接是 arXiv；此处优先提供 ICLR 正式会议页面。

- [ ] 02. Toolformer: Language Models Can Teach Themselves to Use Tools

  引用键：`schick2023toolformer`；状态：已引用；Bib 年份：2023。

  优先阅读：[NeurIPS 2023（正式论文集）](https://proceedings.neurips.cc/paper_files/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html)。

- [ ] 03. ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs

  引用键：`qin2023toolllm`；状态：已引用；Bib 年份：2024。

  优先阅读：[ICLR 2024（官方会议页面）](https://iclr.cc/virtual/2024/poster/18267)。

- [ ] 04. Gorilla: Large Language Model Connected with Massive APIs

  引用键：`patil2024gorilla`；状态：已引用；Bib 年份：2024。

  优先阅读：[NeurIPS 2024（正式论文集）](https://proceedings.neurips.cc/paper_files/paper/2024/hash/e4c61f578ff07830f5c37378dd3ecb0d-Abstract-Conference.html)。

- [ ] 05. API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs

  引用键：`li2023apibank`；状态：已引用；Bib 年份：2023。

  优先阅读：[EMNLP 2023（ACL Anthology）](https://aclanthology.org/2023.emnlp-main.187/)。

- [ ] 06. PAL: Program-aided Language Models

  引用键：`gao2023pal`；状态：已引用；Bib 年份：2023。

  优先阅读：[ICML 2023（PMLR 202）](https://proceedings.mlr.press/v202/gao23f.html)。

- [ ] 07. AgentBench: Evaluating LLMs as Agents

  引用键：`liu2023agentbench`；状态：已引用；Bib 年份：2024。

  优先阅读：[ICLR 2024（官方会议页面）](https://iclr.cc/virtual/2024/poster/17388)。

- [ ] 08. WebArena: A Realistic Web Environment for Building Autonomous Agents

  引用键：`zhou2023webarena`；状态：已引用；Bib 年份：2024。

  优先阅读：[ICLR 2024（官方会议页面）](https://iclr.cc/virtual/2024/poster/17826)。

- [ ] 09. Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection

  引用键：`greshake2023indirect`；状态：已引用；Bib 年份：2023。

  优先阅读：[AISec 2023（ACM 工作坊论文集）](https://doi.org/10.1145/3605764.3623985)。

  核查提示：这是 AISec 工作坊论文，不应写成 ACM CCS 主会论文。

- [ ] 10. Ignore Previous Prompt: Attack Techniques For Language Models

  引用键：`perez2022ignore`；状态：未引用；Bib 年份：2022。

  优先阅读：[arXiv 2022（预印本）](https://arxiv.org/abs/2211.09527)。

  核查提示：arXiv 页面注明 ML Safety Workshop at NeurIPS 2022；未确认独立的正式出版页面，保留全文预印本链接。不要将其写成 NeurIPS 主会论文。

- [ ] 11. Data Validation for Machine Learning

  引用键：`breck2019data`；状态：已引用；Bib 年份：2019。

  优先阅读：[MLSys 2019（论文详情页，含 Bibtex 入口）](https://proceedings.mlsys.org/paper_files/paper/2019/hash/928f1160e52192e3e0017fb63ab65391-Abstract.html)。

  核查提示：官网详情页的作者顺序与正式 PDF 首页不同；当前 Bib 按 PDF 首页列为 Breck、Polyzotis、Roy、Whang、Zinkevich。复制网页 BibTeX 前请核对作者顺序，不要直接覆盖这一差异。

- [ ] 12. Automating Large-Scale Data Quality Verification

  引用键：`schelter2018automating`；状态：已引用；Bib 年份：2018。

  优先阅读：[PVLDB 2018，11(12)（ACM Digital Library 论文详情页）](https://doi.org/10.14778/3229863.3229867)。

  核查提示：DOI 对应标题已通过 Crossref 确认，跳转到 ACM Digital Library 详情页；访问时可能需要完成浏览器验证。

- [ ] 13. Reflexion: Language Agents with Verbal Reinforcement Learning

  引用键：`shinn2023reflexion`；状态：已引用；Bib 年份：2023。

  优先阅读：[NeurIPS 2023（正式论文集）](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)。

- [ ] 14. Self-Refine: Iterative Refinement with Self-Feedback

  引用键：`madaan2023selfrefine`；状态：已引用；Bib 年份：2023。

  优先阅读：[NeurIPS 2023（正式论文集）](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91edff07232fb1b55a505a9e9f6c0ff3-Abstract-Conference.html)。

- [ ] 15. SafeRAG: Benchmarking Security in Retrieval-Augmented Generation of Large Language Model

  引用键：`liang2025saferag`；状态：已引用；Bib 年份：2025。

  优先阅读：[ACL 2025（ACL Anthology）](https://aclanthology.org/2025.acl-long.230/)。

- [ ] 16. Uncovering Competing Poisoning Attacks in Retrieval-Augmented Generation

  引用键：`chen2025poisonarena`；状态：未引用；Bib 年份：2025。

  优先阅读：[KDD 2026（ACM 正式出版 DOI）](https://doi.org/10.1145/3770855.3818119)。

  预印本对照：[arXiv](https://arxiv.org/abs/2505.12574)。

  核查提示：新查到 KDD 2026 正式版本，标题与作者已对照 Crossref 元数据；Bib 当前仍记为 2025 年 arXiv 版本。此处只提供正式版本链接，未修改 Bib。

- [ ] 17. CPA-RAG: Covert Poisoning Attacks on Retrieval-Augmented Generation in Large Language Models

  引用键：`li2025cparag`；状态：未引用；Bib 年份：2025。

  优先阅读：[arXiv 2025（预印本）](https://arxiv.org/abs/2505.19864)。

- [ ] 18. Addressing Corpus Knowledge Poisoning Attacks on RAG Using Sparse Attention

  引用键：`dekel2026sdag`；状态：未引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2602.04711)。

- [ ] 19. The Confidence Dichotomy: Analyzing and Mitigating Miscalibration in Tool-Use Agents

  引用键：`xuan2026confidence`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2601.07264)。

- [ ] 20. MICE for CATs: Model-Internal Confidence Estimation for Calibrating Agents with Tools

  引用键：`subramani2025mice`；状态：已引用；Bib 年份：2025。

  优先阅读：[NAACL 2025（ACL Anthology）](https://aclanthology.org/2025.naacl-long.615/)。

- [ ] 21. RADAR: Benchmarking Language Models on Imperfect Tabular Data

  引用键：`gu2025radar`；状态：已引用；Bib 年份：2025。

  优先阅读：[NeurIPS 2025 Datasets and Benchmarks Track（正式论文集）](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a0434f04b6437e875d52d0b0e25c1729-Abstract-Datasets_and_Benchmarks_Track.html)。

- [ ] 22. MCP-ITP: An Automated Framework for Implicit Tool Poisoning in MCP

  引用键：`li2026mcpitp`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2601.07395)。

- [ ] 23. TRUSTDESC: Preventing Tool Poisoning in LLM Applications via Trusted Description Generation

  引用键：`ye2026trustdesc`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2604.07536)。

- [ ] 24. AgentCanary: A Security Evaluation Framework for Autonomous AI Agents in Real Executable Environments

  引用键：`li2026agentcanary`；状态：未引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2606.10484)。

- [ ] 25. PALADIN: Self-Correcting Language Model Agents to Cure Tool-Failure Cases

  引用键：`vuddanti2025paladin`；状态：已引用；Bib 年份：2025。

  优先阅读：[arXiv 2025（预印本）](https://arxiv.org/abs/2509.25238)。

- [ ] 26. AgentAtlas: Beyond Outcome Leaderboards for LLM Agents

  引用键：`mazaheri2026agentatlas`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2605.20530)。

- [ ] 27. Recoverability Has a Law: The ERR Measure for Tool-Augmented Agents

  引用键：`vuddanti2026err`；状态：未引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2601.22352)。

  核查提示：arXiv 的投稿说明不等于会议录用；此处不将其标为 ICML 已发表论文。

- [ ] 28. Metacognitive Retrieval-Augmented Large Language Models

  引用键：`zhou2024metarag`；状态：已引用；Bib 年份：2024。

  优先阅读：[The Web Conference / WWW 2024（ACM 正式出版 DOI）](https://doi.org/10.1145/3589334.3645481)。

- [ ] 29. RAGRank: Using PageRank to Counter Poisoning in CTI LLM Pipelines

  引用键：`jia2025ragrank`；状态：未引用；Bib 年份：2025。

  优先阅读：[arXiv 2025（预印本）](https://arxiv.org/abs/2510.20768)。

  核查提示：arXiv 页面注明在 ACSAC 2025 以 poster 展示；未确认对应的正式全文出版页面，保留 arXiv 全文链接。Poster 展示不等于主会长文录用。

- [ ] 30. MIRROR: A Hierarchical Benchmark for Metacognitive Calibration in Large Language Models

  引用键：`wang2026mirror`；状态：未引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2604.19809)。

- [ ] 31. Automated structural testing of LLM-based agents: methods, framework, and case studies

  引用键：`kohl2026structural`；状态：未引用；Bib 年份：2026。

  优先阅读：[IEEE BigData 2025（IEEE 正式出版 DOI）](https://doi.org/10.1109/bigdata66926.2025.11401679)。

  预印本对照：[arXiv](https://arxiv.org/abs/2601.18827)。

  核查提示：新查到 IEEE BigData 2025 正式版本，标题与作者已对照 Crossref 元数据；Bib 当前仍记为 2026 年 arXiv 版本。会议年份与预印本上线年份不同，此处未修改 Bib。

- [ ] 32. Sell Me This Stock: Unsafe Recommendation Drift in LLM Agents

  引用键：`wu2026agentdrift`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2603.12564)。

- [ ] 33. AgentSentry: Mitigating Indirect Prompt Injection in LLM Agents via Temporal Causal Diagnostics and Context Purification

  引用键：`zhang2026agentsentry`；状态：未引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2602.22724)。

  核查提示：arXiv 页面注明 under review；不据此推断正式录用。

- [ ] 34. Co-Sight: Enhancing LLM-Based Agents via Conflict-Aware Meta-Verification and Trustworthy Reasoning with Structured Facts

  引用键：`zhang2025cosight`；状态：未引用；Bib 年份：2025。

  优先阅读：[arXiv 2025（预印本）](https://arxiv.org/abs/2510.21557)。

- [ ] 35. Proof-of-Use: Mitigating Tool-Call Hacking in Deep Research Agents

  引用键：`ma2025pou`；状态：未引用；Bib 年份：2025。

  优先阅读：[arXiv 2025（预印本）](https://arxiv.org/abs/2510.10931)。

- [ ] 36. Auditing Automated Evaluation, Error Propagation, and Runtime Mitigation in Tool-Using Language Agents

  引用键：`gurram2026agentprop`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2604.16706)。

- [ ] 37. ToolCritic: Detecting and Correcting Tool-Use Errors in Dialogue Systems

  引用键：`hamad2025toolcritic`；状态：已引用；Bib 年份：2025。

  优先阅读：[arXiv 2025（预印本）](https://arxiv.org/abs/2510.17052)。

- [ ] 38. RAGShield: Detecting Numerical Claim Manipulation in Government RAG Systems

  引用键：`patil2026ragshield`；状态：未引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2604.00387)。

- [ ] 39. Tools Fail: Detecting Silent Errors in Faulty Tools

  引用键：`sun2024toolsfail`；状态：已引用；Bib 年份：2024。

  优先阅读：[EMNLP 2024（ACL Anthology）](https://aclanthology.org/2024.emnlp-main.790/)。

- [ ] 40. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents

  引用键：`debenedetti2024agentdojo`；状态：已引用；Bib 年份：2024。

  优先阅读：[NeurIPS 2024 Datasets and Benchmarks Track（正式论文集）](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html)。

- [ ] 41. PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models

  引用键：`zou2024poisonedrag`；状态：已引用；Bib 年份：2025。

  优先阅读：[USENIX Security 2025（官方会议页面）](https://www.usenix.org/conference/usenixsecurity25/presentation/zou)。

- [ ] 42. Beyond Function Calling: Benchmarking Tool-Using Agents under Tool-Environment Unreliability

  引用键：`tian2026toolbenchx`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2606.25819)。

- [ ] 43. ToolRobustBench: Stage-Wise Perturbation Evaluation and Failure Diagnosis for Tool-Calling Agents

  引用键：`zheng2026toolrobustbench`；状态：已引用；Bib 年份：2026。

  优先阅读：[arXiv 2026（预印本）](https://arxiv.org/abs/2608.23635v1)。

  核查提示：保留 Bib 指定的 v1，核对时注意不要把后续版本内容混入当前引用。

- [ ] 44. Beyond the Final Answer: Evaluating the Reasoning Trajectories of Tool-Augmented Agents

  引用键：`kim2025trace`；状态：已引用；Bib 年份：2026。

  优先阅读：[ICML 2026（官方会议页面）](https://icml.cc/virtual/2026/poster/64255)。

  核查提示：提供已确认的 ICML 2026 官方会议页面；不推测尚未核实的 PMLR 卷号或页码。

- [ ] 45. DAComp: Benchmarking Data Agents across the Full Data Intelligence Lifecycle

  引用键：`lei2025dacomp`；状态：已引用；Bib 年份：2025。

  优先阅读：[arXiv 2025（预印本）](https://arxiv.org/abs/2512.04324v1)。

  核查提示：保留 Bib 指定的 v1，核对时注意版本一致性。

- [ ] 46. palmerpenguins: Palmer Archipelago (Antarctica) Penguin Data

  引用键：`horst2020palmerpenguins`；状态：已引用；Bib 年份：2020。

  优先阅读：[数据集 / R 软件包（项目官方页面）](https://allisonhorst.github.io/palmerpenguins/)。

  核查提示：数据资源而非论文。另见 [归档 DOI](https://doi.org/10.5281/zenodo.3960218) 和 [官方推荐引用](https://allisonhorst.github.io/palmerpenguins/authors.html)。

- [ ] 47. Auto MPG

  引用键：`quinlan1993autompg`；状态：已引用；Bib 年份：1993。

  优先阅读：[数据集（UCI 官方页面）](https://archive.ics.uci.edu/dataset/9/auto+mpg)。

  核查提示：数据资源而非论文；核对数据集名称、贡献者及 UCI 推荐引用。

- [ ] 48. Bike Sharing

  引用键：`fanaee2013bikedata`；状态：已引用；Bib 年份：2013。

  优先阅读：[数据集（UCI 官方页面）](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset)。

  核查提示：数据资源而非论文；核对数据集引用与介绍该数据集的研究论文是否被混用。

## 本次额外发现的版本差异

以下两条当前均未在论文中引用，Bib 仍保留预印本信息。本清单已优先列出查到的正式版本，是否同步更新 Bib 可在人工核对后决定。

- 第 16 条 `chen2025poisonarena`：2025 年预印本已有 KDD 2026 正式版本。[Crossref 出版元数据](https://api.crossref.org/works/10.1145/3770855.3818119)。
- 第 31 条 `kohl2026structural`：2026 年上线的预印本对应 IEEE BigData 2025 正式版本。[Crossref 出版元数据](https://api.crossref.org/works/10.1109/bigdata66926.2025.11401679)。

引用键中带有的年份只是内部标识，不一定等于正式发表年份；核查年份时应看 Bib 的 `year` 字段和出版方信息，不必仅为年份差异重命名引用键。
