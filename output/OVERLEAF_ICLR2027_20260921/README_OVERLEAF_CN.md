# Overleaf 完整论文源码包

本包是 2026-09-21 本地论文的独立副本，包含编译所需的章节、图片、参考文献、实验结果表格和官方 ICLR 2027 模板，不需要原仓库或模型 API。

## 上传和编译

1. 在 Overleaf 选择 **New Project → Upload Project**，直接上传配套 ZIP。建议新建项目，不要与以前的模板和缓存混用。
2. 打开项目设置，将 **Main document** 设为根目录的 `main.tex`。不要选择 `iclr2027/iclr2027_conference.tex`，它只是官方示例。
3. 将 **Compiler** 设为 **XeLaTeX**，TeX Live 选择平台提供的最新稳定版本。
4. 点击 **Recompile**。如果出现旧缓存问题，选择 **Recompile from scratch**。
5. 等待参考文献及交叉引用的多轮编译完成，再下载 PDF。

`latexmkrc` 提供 XeLaTeX 默认设置及官方依赖搜索路径；不需要启用 shell escape，也不需要安装字体或转换 SVG。

## 文件说明

- `main.tex`：唯一论文入口，采用匿名审稿模式。
- `sections/`：完整章节目录。只有由 `main.tex` 及其子文件引用的章节参与编译，其余历史章节不生效。
- `figures/`：当前正文及附录使用的全部 PDF 图、两个 LaTeX 表格文件，以及可用的对应 SVG 编辑源文件。论文只加载 PDF 图。
- `iclr2027/`：仓库中的官方模板文件，未经改动。其示例 `.tex` 和 `.bib` 不参与论文编译。
- `references.bib`：本论文实际使用的参考文献库。
- `output/`：四个被附录直接加载的实验结果表格文件，必须保留路径，不要删除。

没有打包 API 密钥、实验原始日志、人工标注原件、旧图片版本或本地编译缓存。此包用于 Overleaf 编辑，不替代完整的实验复现仓库，也不是已经完成全部投稿核查的材料包。

## 本次论文内容

结尾顺序为 **Conclusion → Limitations → AI use statement → References → Appendix**。

AI use statement 的正文按照作者要求留空，请在 `sections/12_ai_use_statement.tex` 中自行填写，提交前不能保持空白。标题、实验数值和官方样式均未为打包而修改。

本地原论文目前研究正文（含 Limitations）结束于第 9 页。不同 TeX Live 版本的换行可能有细微差异，请在 Overleaf 编译后再次确认页数和引用。AI use statement 不计入正文页数。

本机使用 Tectonic（基于 XeTeX）验证独立源码构建；这不等同于已登录 Overleaf 完成在线测试。若仍报错，请提供第一条红色错误及其前后日志，避免只提供最后的“No PDF”。
