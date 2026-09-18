# Figure 1 / Figure 2 的无损 PDF 导出

当前 `figure1.pdf`、`figure2.pdf` 来自同名 PNG，保留原始 5504×3072 像素。
PNG 原文件没有修改。没有重绘、锐化、上采样、OCR 替字、裁剪或更换字体。
第一张 PNG 的 alpha 通道全部为不透明，去掉这个冗余通道不会改变可见像素。

PDF 使用无损 Flate 压缩，没有 JPEG 重压缩。导出后重新提取 PDF 中的图片，
与原 PNG 的 RGB 像素逐字节比较；结果写入 `figure_pdf_export.json`。
这两个 PDF 作为旧版保留；LaTeX 现引用另行重建的 `figure1_vector.pdf`、
`figure2_vector.pdf`。新版本说明见 `FIGURE_VECTOR_NOTES_CN.md`。

## 清晰度的边界

这两个文件是**包含高分辨率位图的 PDF，不是真矢量图**。
换容器格式不会创造原图没有的细节，也不能把已经栅格化的文字变回可编辑字体。
ICLR 模板实际正文宽度为 5.5 英寸（396 pt），因此当前图片的有效分辨率约
为 1001 dpi。按稿件尺寸阅读时，更值得关注的是小字字号、拥挤程度和原始字体边缘，
不是仅看扩展名。原 PNG 如果已经被完整嵌入论文，改为此 PDF 不会产生额外细节。

## 字体建议

- 不建议为了“像大模型论文”而换成 Comic Sans MS；它是手写风格，不是会议图表规范。
- 这两张图信息密集，若以后有 SVG/PPTX/绘图源文件，建议统一使用 Arial/Helvetica
  一类清晰的无衬线字体，减少过窄字体；代码片段保留等宽字体。
- 正文使用 Times 系列，不意味着图中的所有文字也必须换 Times New Roman。
  若采用 Times，应在可编辑源文件中统一重排，并按论文实际尺寸检查小字可读性。
- 当前没有找到匹配这两张图的可编辑矢量源文件。仅有 PNG 时，换字体需要重建
  文字与布局，不能再声称外观逐像素不变。因此此次保留原字体。

## 复现

```bash
# 只检查现有 PDF 与 PNG 的像素、比例是否一致：
python3 toxictool_bench/export_figure_pdfs.py --verify-only
# 以后更新 PNG 后，明确重新生成派生 PDF：
python3 toxictool_bench/export_figure_pdfs.py --replace
```

真正的矢量清晰度需要从 SVG、PPTX、draw.io、Illustrator 或绘图代码导出 PDF，
或另行批准重建可编辑图稿；不建议自动描摹现有小字来冒充矢量文字。
