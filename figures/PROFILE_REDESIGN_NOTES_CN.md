# 算子与跨模型结果：简洁排版试用版

本次仅改变呈现方式，不修改原始结果、均值口径或四舍五入规则。

- `fig_operator_dots.pdf` / `.svg`：正文使用三面板横向点图，依次展示 poisoned TSR、
  BCR、VR/RR。共同的算子行按数值与语义任务分组，横轴统一为 0–1。
  VR 是蓝色圆点，RR 是赭色空心菱形，两者稍作纵向错位以免重叠，不用连线暗示因果漏斗。
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
python3 toxictool_bench/plot_paper_figures.py --table-redesign-only --preview-dir figures/preview
python3 -m pytest toxictool_bench/tests/test_paper_profile_redesign.py -q
python3 toxictool_bench/check_paper_static.py --main main.tex
tectonic -Z search-path=iclr2027 main.tex --outdir output/scorer_revision_v2/pdf --keep-logs --keep-intermediates
```

完整运行 `plot_paper_figures.py` 也会更新这些新产物。不要手工修改生成的两份表格文件；
应修改绘图脚本或经过研究流程确认的源数据，再重新生成。
