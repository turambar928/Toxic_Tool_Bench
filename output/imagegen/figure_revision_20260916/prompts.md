# Figure edits — 2026-09-16

Mode: built-in image_gen, editing the original PNGs. Original assets are preserved.

## Figure 1

Use case: text-localization and precise-object-edit.
Edit target: the supplied original Figure 1 PNG, an academic ToxicBench infographic. Make a revised finished figure, not a redesign. Preserve its very wide landscape aspect ratio, navy header, white background, rounded boxes, blue agent block, green clean branch at bottom left, red poisoned branch at bottom right, and original illustration/icon style. High resolution, crisp readable typesetting. No extra claims or text beyond this specification. Rewrite all text legibly; remove any gibberish in original code. Keep all elements inside canvas.

Exact replacement text and placement:
Top navy banner: "Figure 1 | Silent Tool Poisoning: An Example".
USER QUERY heading and query unchanged: "Which store had the highest revenue last quarter, and what was it?"
Middle blue agent heading: "DATA AGENT WITH TOOL ACCESS". Inside: "Data Agent" and "LLM + Tool Calls".
Attached small tool box heading "REGISTERED TOOL"; inside only "csv_tool(query)".
Upper right data panel: "DATA SOURCE"; columns "Store" and "Q4 Revenue"; rows "Store A  $230,000", "Store B  $450,000", "Store C  $310,000". Highlight Store B with "highest". Arrow label "READS" and "(stores.csv)" unchanged. This source table is clean and must not look poisoned.

Bottom left green heading "PATH 1: CLEAN ENVIRONMENT".
Its left box title "CSV Tool"; simple readable code:
row = stores.loc[stores["Q4 Revenue"].idxmax()]
return row["Store"], row["Q4 Revenue"]
Its middle box text "Original Tool Output" and "No Modification".
Its right box "Store B — $450,000" and "Correct Observation".
Green bottom badge "CORRECT STORE–VALUE PAIR".

Bottom right red heading "PATH 2: POISONED ENVIRONMENT".
Upper yellow box title "TOOL-OUTPUT POISONING".
Exactly three bullets:
"The original tool runs successfully."
"The proxy swaps Store A and Store B in the output."
"No exception, error, or warning is shown."
To the right within this yellow box replace both old function/code examples with two small output cards joined by arrow labeled "Label swap":
left "Original output" / "Store B — $450,000";
right "Modified output" / "Store A — $450,000".
Below yellow box the red section heading "MODIFIED TOOL OBSERVATION".
Its three connected boxes left to right:
"Original Tool Output" / "Store B — $450,000";
"Output Proxy" / "Swap Store Labels";
"Store A — $450,000" / "Observation Received by the Agent".
Bottom red badge "WRONG STORE–VALUE PAIR".
Bottom standalone sentence: "A Successful Tool Call Can Return a Plausible but Wrong Observation".

Scientific invariants: only returned tool observation is modified; original tool executes successfully and source data remain unchanged. Remove all old wording about registry poisoning, replaced tool logic, poisoned tool executor, undetectable action. Retain original structure and visual identity, while gently resizing internal text areas for legibility. No watermarks.

### Punctuation correction

undefined

## Figure 2

Use case: text-localization and precise-object-edit.
Edit target: original Figure 2 ToxicBench PNG. Produce a finished edited academic infographic based closely on this image. Preserve landscape aspect ratio, navy section bars, white background, four stacked sections A/B/C/D, top blue and purple task panels, green/red environment panels, colorful metric cards, and bottom four colored cards. Preserve matching original icon illustration style. All text below must be correctly spelled, sharp and readable. Reflow within existing boxes as needed, do not invent any scientific claims or numbers. High resolution. No watermarks.

TOP BANNER:
left "Data Agents"
center "Figure 2 | ToxicBench: Benchmark and Verification Protocols"
right "Tool-output Poisoning"

SECTION A:
left section title "A  Task Suites".
center section subtitle "Cross-model: 58 Tasks | Expanded: 120 Tasks | Multi-table: 13 Tasks".
Blue panel heading "Numerical Tasks"; secondary line "Cross-model: 34 tasks | 11 CSV datasets".
Purple panel heading "Semantic / Schema Tasks"; secondary line "Cross-model: 24 tasks | 17 datasets".
In both panels use small label "Operators across the benchmark:".
Numerical six operator cells: first row "Aggregate Scale", "Sign Flip", "Rank Swap"; second row "Ratio Inversion", "Denominator Swap", and last cell two lines "Omit Filter" / "Unit Conversion".
Semantic five operator cells: "Label Swap", "Treatment/Control Flip", "Biased Retrieval", "Column-Semantic Swap", "Stale Metadata". No extra duplicated Biased badge.

SECTION B:
left section title "B  Paired Evaluation Protocol"; center "Same Query and Source Data".
Left green panel "Clean Environment". Agent and tool icons kept; tool call arrow labeled "Tool Call"; returned-observation label "Original Output". Agent label "Data Agent"; tool label "Tool".
Middle panel title "Matched Task Pair". Three compact text groups:
"Same query" / "Same source data";
"Same model and adapter" / "Same execution budget";
"Compare Answers and Trajectories".
Remove original obscure formulas, crossed diamond, vc circle, Isolation Control and data flow wording. Use simple comparison icon if needed.
Right red panel "Poisoned Environment", central label "Modify Returned Observation", proxy label "Tool-output Proxy", warning strip "No Exception or Warning", bottom note "Source Data Unchanged".
Do not depict a corrupted source database: show corruption marks on an output document/card near the proxy; underlying database clean.

SECTION C:
left section title "C  Evaluation Metrics"; center "Task Success and Evidence Use".
Preserve six colorful cards, with precisely this content left to right:
1 blue: "TSR" / "Task Success Rate" / "All Runs".
2 red: "PAR — Poisoned-answer Adoption" / "VPA — Adoption after Validation".
3 orange: "BCR" / "Blind Compliance Rate".
4 purple: "ADR — Anomaly Detection" / "VR — Evidence Validation".
5 green: "RR" / "Recovery Rate".
6 gray: "Human Audit" / "240 Trajectories" / "Two Annotators + Adjudication".
Only cards 2,3,4,5 have small top badge "EXPOSED RUNS ONLY". Card1 and card6 have no exposure badge.
Remove old 58/60, delta TSR, Performance Drop and other old card labels entirely.

SECTION D:
navy bar left "D  Verification Protocols"; center "Controlled Method Comparison"; green strip right "Matched Per-route Step and Token Limits".
Keep four bottom colored cards and their numbers but make them four PARALLEL methods; remove all arrows between these four cards. Keep simple tool/agent icons without extra text. Discard old expectation subicons, monitoring gadgets, scanning gates and agree/disagree lists to give text space.
Card1 blue:
"1  Base"
"One ordinary route"
"Solve the task with tools."
"Final answer:"
"Route 1 answer"

Card2 orange:
"2  Double-pass"
"Two ordinary routes"
"Route 2 starts without"
"the Route 1 answer."
"Final answer:"
"Route 2 answer"

Card3 purple:
"3  Verification-only"
"Ordinary route + verification route"
"Route 2 checks the first answer"
"as an untrusted claim."
"Final answer:"
"Route 2 answer"

Card4 green:
"4  Generic Guard"
"Expectation prompt + verification route"
"Route 1 receives a generic expectation."
"Route 2 checks the first answer."
"Final answer:"
"Route 2 answer"

Absolutely REMOVE all claims "fully mitigated", "BCR: 0.11 → 0.00", "Independent evidence", "Returns verified", "Evidence Gating", "Verifiable Execution", and GVP. Do not claim a defense guarantees correctness. Preserve original figure's visual identity and panel structure with clear English and adequate whitespace.

