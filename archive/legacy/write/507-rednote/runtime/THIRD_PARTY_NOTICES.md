# Runtime third-party notices

The browser bundle contains the following unmodified library code bundled with project-authored modules:

- marked 18.0.10, MIT, <https://github.com/markedjs/marked>
- DOMPurify 3.4.14, used under Apache-2.0, <https://github.com/cure53/DOMPurify>

esbuild 0.28.2 is an MIT-licensed development dependency used to produce the bundle and is not embedded in it: <https://github.com/evanw/esbuild>.

The runtime also includes these unmodified official browser fonts:

- Adobe Source Han Sans CN Variable 2.005R, SIL Open Font License 1.1, `fonts/SourceHanSansCN-VF.otf.woff2`, SHA-256 `7087698d52240614659957608d8c4ad446759aee3208409dc9f566412e7af8f4`, <https://github.com/adobe-fonts/source-han-sans/blob/release/Variable/WOFF2/OTF/Subset/SourceHanSansCN-VF.otf.woff2>
- Adobe Source Han Serif CN Variable 2.003R, SIL Open Font License 1.1, `fonts/SourceHanSerifCN-VF.otf.woff2`, SHA-256 `808cb3203bb9cdd6b166a8a656a0c7608a7dc2a31c41c2cd0374550cae445471`, <https://github.com/adobe-fonts/source-han-serif/blob/release/Variable/WOFF2/OTF/Subset/SourceHanSerifCN-VF.otf.woff2>

The corresponding copyright notices and complete license texts are distributed as `fonts/OFL-Source-Han-Sans.txt` and `fonts/OFL-Source-Han-Serif.txt`. The OFL permits use, embedding and bundling with commercial software subject to its conditions; the fonts may not be sold by themselves.

Full license texts are available in each pinned npm package and its upstream repository. Exact package integrity values are recorded in `package-lock.json`.
