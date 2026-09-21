# 独立源码构建检查

检查日期：2026-09-21。

- 将本包复制到仓库之外的新临时目录，未复制原仓库的 `.aux`、`.bbl`、`.log` 或编译 PDF。
- 在该目录执行 `tectonic main.tex --keep-logs --keep-intermediates`，构建成功。
- 再执行 `tectonic -Z search-path=iclr2027 main.tex --keep-logs --keep-intermediates`，优先使用包内官方模板依赖，构建成功。
- PDF 共 27 页，纸张为 US Letter；Conclusion 和 Limitations 均在第 9 页，AI use statement 和参考文献从第 10 页开始。
- 最终日志未发现 undefined reference/citation 或 Overfull 警告；仍有原有的 Underfull 排版提示及 Tectonic 的 BibTeX 重跑提示，不能称为完全无警告构建。
- 主文件、完整章节目录及官方模板目录与打包时仓库版本逐文件比较一致。
- 对包内 TeX、BibTeX、Markdown 和编译配置执行常见密钥及本机绝对路径模式检查，未命中；此检查不等同于全面安全审计。
- `latexmkrc` 通过 Perl 语法检查。

本机没有 Overleaf 在线环境，未声称完成在线测试。Overleaf 请使用 `main.tex`、XeLaTeX 和平台可用的最新稳定 TeX Live；上传后再次确认页数和引用。
