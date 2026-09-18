# Figure 1 / Figure 2：SVG 矢量重建版

## 文件与版本

| 图 | 可编辑源文件 | 投稿用矢量 PDF | 保留的旧版 PDF |
| --- | --- | --- | --- |
| Figure 1 | `figure1_vector.svg` | `figure1_vector.pdf` | `figure1.pdf` |
| Figure 2 | `figure2_vector.svg` | `figure2_vector.pdf` | `figure2.pdf` |

同名原始 PNG 和旧版 PDF 均未覆盖。旧版 PDF 是无损嵌入 PNG 的位图版本；
新版本重新绘制为 SVG 文字、路径和几何图形，再通过 librsvg/Cairo 导出 PDF。
不是把 PNG 塞入 SVG，也不是将模糊的像素轮廓自动描摹成路径。

论文 `sections/03_toxictool_bench.tex` 已引用新版本，宽高比例不变。
若需切回旧版，只需将两处 `figureN_vector.pdf` 改回 `figureN.pdf`。

## 内容与字体

保留原图的任务问题、Store/收入数值、任务数量、指标名称、模块分区和流程关系。
保留第二路线答案被选用、仅修改返回观察而不修改源数据等核心信息。
装饰图标由矢量形状重新绘制；配色和布局延续原图，但不是逐像素复刻。
原图中的多余引号及明显拼写瑕疵作了排版清理，长句适当换行。

图中文字统一为 **Arial**，代码为 **Courier New**。不使用 Comic Sans MS；
正文的 Times 字体不要求流程图也必须使用 Times New Roman。
SVG 中保留可编辑文字，因此跨机器编辑时需安装相应字体，否则可能发生替换和重排；
PDF 已嵌入字体子集，阅读和投稿不依赖接收方安装字体。

矢量化解决放大后文字、边框、箭头模糊的问题，不会增加版面空间。
两图仍然信息密集，按论文 5.5 英寸宽度打印时，一些辅助标签依然较小；
若以后要求明显增大这些小字，需要另行精简内容或拆图，此次未做这类内容调整。

## 复现与检查

从仓库根目录运行：

```bash
python3 toxictool_bench/rebuild_vector_figures.py
python3 -m pytest toxictool_bench/tests/test_vector_figures.py -q
pdfimages -list figures/figure1_vector.pdf
pdfimages -list figures/figure2_vector.pdf
pdffonts figures/figure1_vector.pdf
pdffonts figures/figure2_vector.pdf
```

生成环境需要 Python 的 `gi`/PyGObject、`cairo`、`Pillow`、`pypdf`，
系统 librsvg，以及 `/usr/share/fonts/truetype/msttcorefonts` 中的 Arial/Courier New。
当前环境使用 librsvg 2.52。仅使用现成 PDF 编译论文不需要这些生成依赖。

脚本会重新生成四个 `_vector` 文件与 `vector_rebuild_manifest.json`，
并在前后核对原 PNG/PDF 的 SHA256。修改布局应优先编辑生成脚本；
如直接编辑 SVG，请先另存副本，避免下次运行脚本覆盖手工改动。

验证要求：SVG 没有 `<image>` 或外部图像引用；PDF 没有位图对象；文字可提取；
字体嵌入；任务数量和关键文案保留；原文件哈希不变。清单记录各输出哈希及文字元素。
