# 算子与跨模型结果：简洁排版试用版

本次仅改变呈现方式，不修改原始结果、均值口径或四舍五入规则。

配色依据（2026-09-20 查阅）：顶刊没有统一的专用色板，应按数据类型选择色阶。
本图为 0–1 原始率，选用单向顺序色阶，而非有中心值含义的发散色阶或分类调色板。
这里使用 Matplotlib 实现的 ColorBrewer `Blues`，不宣称其严格感知均匀；测试检查了
明度单调递减，并保留全部数字以避免仅靠色差读数。

- Nature Methods, [Points of view: Color blindness](https://www.nature.com/articles/nmeth.1618)：关注色觉障碍读者的可辨识性。
- Nature Communications, [The misuse of colour in science communication](https://www.nature.com/articles/s41467-020-19160-7)：说明彩虹色、不均匀色阶及红绿组合的风险。
- [ColorBrewer 色阶选择说明](https://colorbrewer2.org/learnmore/schemes_full.html)：顺序色阶适合从低到高的有序数据，用明度表达大小。

- `fig_operator_heatmap.pdf` / `.svg`：正文 Figure 3 使用统一色阶热力图，四列分别为
  poisoned TSR、BCR、VR、RR，无子图编号。采用 ColorBrewer `Blues` 浅蓝—深蓝顺序色阶，
  全图共用 0–1 原始率尺度，不逐列归一化、不倒转 BCR；颜色深不代表所有指标都更好。
  所有单元格直接标注数值，所有行等距排列，无任务族间的额外留白，字体保持 Times 系。
  热力单元格和色条均为原生矢量，PDF 不嵌入栅格图像。
- `fig_operator_bars.pdf` / `.svg`：保留上一版横向条形图，正文已不再引用。
- `fig_operator_dots.pdf` / `.svg`：保留上一版点图用于历史对比，正文已不再引用。
- `operator_profile_table.tex`：附录原生三线表，保留全部 TSR/BCR/VR/RR/PDR 数值。
  正文不再使用这张表；PDR 与投毒送达口径仍可在附录核查。
- `fig_cross_model_paired.pdf` / `.svg`：两个任务族各一个面板，空心点表示 clean TSR，
  蓝色实心点表示 poisoned TSR，连线表示两者差异。坐标统一为 0–1 附近，
  不用连线冒充置信区间。每个点仍为三个 adapter 的未加权均值。
- `cross_model_rates_table.tex`：保留六行跨模型结果中的 clean/poisoned TSR、BCR 和 PDR。
  原生表格与图使用同一批输入数据，避免手工复制数值。

旧版 `fig_operator_profile.pdf`、`fig_cross_agent_model.pdf` 未覆盖，便于对比。
正文与附录已改为引用新版；自动更新表图编号，无须手工编号。

复现：

```bash
python3 toxictool_bench/plot_paper_figures.py --operator-heatmap-only --preview-dir figures/preview
python3 toxictool_bench/plot_paper_figures.py --table-redesign-only --preview-dir figures/preview
python3 -m pytest toxictool_bench/tests/test_paper_profile_redesign.py -q
python3 toxictool_bench/check_paper_static.py --main main.tex
tectonic -Z search-path=iclr2027 main.tex --outdir output/scorer_revision_v2/pdf --keep-logs --keep-intermediates
```

完整运行 `plot_paper_figures.py` 也会更新这些新产物。不要手工修改生成的两份表格文件；
 应修改绘图脚本或经过研究流程确认的源数据，再重新生成。
