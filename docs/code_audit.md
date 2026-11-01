> Historical note from the earlier release. For the current importer, workbook label audit, and figure checks, see [the release README](../README_EN.md) and [design notes](studio_design.md).

# 源码审计记录

原始来源：用户 Google Drive 文件夹“全球价值链贸易核算matlab程序（TIVA，WWZ分解方法大全）以及区域表链接方法”。已获取源程序和 2007 年数据文件副本；原始文件保留于 `data/`。

`valueadded2007.m`（554 行，原始 GB18030 编码）：S=48，N=17；从 `2007global.xlsx` 的 `Sheet2` 取 816×816 中间投入、816×144 最终需求、增加值和总投入；计算 A、全球 Leontief inverse B、局部 L、出口中间产品 tt2–tt9；第 281–519 行定义 T1–T16；第 521–549 行核对双边产业总出口恒等式。已迁移为 `src/gvc/engine.py` 并在原始 2007 年输入上验证。

`tradeinvalueadded2007.m`（709 行）：包含 TIVA、增加值相关贡献计算，显式循环中国区域编号 7–14（源程序 1-based）。该程序未独立迁移或验证。保留源文件。

`GVCDVC.m`（244 行）：包含与增加值相关的区域路径计算，保留未迁移。

原始 2007 年的 16 个 `T?va2007.csv` 为 816×48，每行指向一个出口方/行业组合，每列指向进口地；原始导出采用有限有效数字。源 `CHECKva2007.csv` 有 799 行（源程序从 MATLAB cell 中导出时省略了空的对角分块），新引擎使用完整形状 816×48 和明确的对角置零方式。

其他工作簿包括区域链接示例表 `2007年WIOT与中国区域表的联接2倪红福.xlsx`。它未作为当前 WWZ 2007 复现的直接输入，不能认为链接程序已完成移植。

`terms_source_dictionary.csv` 记录 16 项从源程序抄录的矩阵公式和行号。部分经济意义描述直接基于 tt2–tt9 的原始代码注释，仅用于源码导航，并非未经核对的权威 WWZ 术语对应表。

核算公式中 N 个产业按经济体连续排列，Y 在每个目的地将 3 个最终需求类别加总。双边指标不可随意重新排列或跨会计层级求和。当前验证仅覆盖 2007 年 48×17 的历史结构以及自动生成的小型一致性用例。
