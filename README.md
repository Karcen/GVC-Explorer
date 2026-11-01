# GVC Explorer · 全球价值链图谱

[English](README_EN.md) · [离线公式手册](docs/formulas_zh.html) · [Jiacheng Zheng](https://karcen.github.io/)

给定出口经济体、进口经济体和出口行业，GVC Explorer 把这笔总出口分成 WWZ 的 16 项。桌面程序读取新的投入产出表；离线网页只读已经算好的结果。二者共用同一套数值和名称。

桌面、离线图谱和公式手册使用固定的白灰色界面。蓝色标出主要操作和当前选项。

## 开始使用

先看结果：解压，双击 `offline_dashboard.html`。默认展示 2007 年德国对美国的全部行业出口。可以切换中文或 English、改变贸易方向、点热图选行业和目的地，也可以保存当前双边分解的 CSV。不需要联网或安装 Python。

分析新表：解压完整 ZIP，用带 Tk 的 Python 3.10 或更高版本在编辑器（如 VS Code、PyCharm 或 IDLE）中运行 `run_all.py`。依赖已齐就直接进入桌面。否则启动器会检查项目的 `.venv`；仍缺包时，先询问是否安装到这个目录，不改系统 Python。无需打开 `.command` 或 `.bat`。下载缺少的包需要联网，分析不需要。

也可以在编辑器使用的 Python 环境里一次装齐桌面依赖，再运行 `run_all.py`：

```bash
python -m pip install "numpy>=1.24,<3" "scipy>=1.10,<2" "lxml>=4.9,<7" "pandas>=2,<3" "plotly>=5,<7" "matplotlib>=3.7,<4" "fonttools>=4.39,<5"
```

在桌面左栏点“导入年度表或 ZIP”。首次试用可选 `examples/fixture_3area_3sector.csv`：这是含负库存变动和产品税净额的教学模拟表，不是 OECD 观测数据。结果写入 `runs/` 下单独的运行目录；“选择输出位置”可更改目录。默认图使用界面当前语言。切换语言或筛选后，用“导出当前筛选的全部图”另存，不会覆盖第一次导出。

```bash
python studio_batch.py examples/fixture_3area_3sector.csv --output runs --language zh
```

## 输入与核算口径

年度文件接受带代码的 OECD 式宽表：CSV、CSV.GZ、装有年度 CSV 的 ZIP。行是供应行业，列是使用行业；`AUS_C26` 这类代码用于对齐行列，顺序可以不同。每个目的地需要 HFCE、NPISH、GGFC、GFCF、INVNT 和 DPABR 六类最终需求，以及全表的增加值行、总产出行与列。程序保留负库存变动，拒绝重复代码、缺失交易、不能识别的分类和超过容差的收支差额。该入口按百万美元解释数据。其他单位请用标准矩阵目录导入。

有 TLS 行且产品税减补贴非零时，软件用 VA＋TLS 与总产出核对。此时结果分摊的是“增加值加产品税净额”，不能报告为纯增加值。全国口径只用中国、墨西哥的合计项，不重复加总企业拆分项；没有可用全国合计的拆分表不予计算。经济体、行业字典对应随包的 2025 Extended 代码表，不代表任意年份或版本都能直接导入。

另可读取随包的 `2007global.xlsx`，或按“经济体 → 行业”排列的 `Z.csv`、`Y.csv`、`VA.csv`、`X.csv` 和 `metadata.json` 目录。四个矩阵均不应有表头；Y 每列对应一个目的地。元数据需提供与矩阵位置相符的 `country_names`、`industry_names`，以及实际单位 `unit`；缺少可信标签时不按位置猜测。通用目录按用户提供的名称显示，不自动翻译任意自定义名字。

## 2007 年的国家、地区与行业

48 个经济体／地区和 17 个行业的名称来自 `2007global.xlsx` 的 Sheet1。将其与 MATLAB 读取的 Sheet2 对照，665,856 个中间投入单元格和 117,504 个最终需求单元格逐值相同；C4 标明单位为百万美元。代码保留工作簿原写法。中国八个区域在该样例中是独立核算单元，跨区域流量计入跨单元贸易，不能直接解读为中国对外贸易。详见 [原表核对记录](reports/legacy_axis_audit.json)。

## 图形和结果文件

每次导入后生成八张图：十六项分解、五类分组、出口目的地、双边行业构成、行业与目的地热图、双向贸易、各经济体进出口和主要双边流向。每张都有 PDF、PNG、SVG 和图源 CSV。热图按出口额选取最多八个行业、十个目的地，颜色表示所选分解项的金额，不是份额。进出口散点图和主要流向图涵盖全部经济体，不限于当前选中的贸易伙伴。每个图题下标明实际筛选范围。

每张 PDF 保存后会运行 nature-figure 上游的字号检查脚本；低于 6.5 pt 不通过。结果保存在图形目录的 `nature_text_audit.json`。

`atlas.html` 是本次结果的双语离线图谱；`results.npz` 保存未舍入的数组；`metadata.json` 记轴名和口径；`manifest.json` 记输入哈希、核算残差、软件版本和输出文件哈希。`reports/atlas_2007/zh/` 和 `en/` 中已附中英文基准图样。

## WWZ 16 项分解：公式与经济含义

以下采用原 MATLAB 程序 `valueadded2007.m` 中的 T1–T16 顺序，与 Wang、Wei 和 Zhu（2013）附录 E 的 Table E1 一一对应。分解对象是出口经济体 $s$ 向进口经济体 $r$ 的**逐产业总出口向量**，而非某个产业创造的全部增加值。16 个分量均为 $N\times1$ 向量；选定产业后，Dashboard 显示相应的标量。

### 记号

- $s$ 为出口经济体，$r$ 为直接进口经济体，$t,u$ 为用于追踪后续生产或最终吸收的其他经济体，且 $s\ne r$；$N$ 为每个经济体的产业数。
- $Z^{sr}$ 为 $s$ 的产品供给 $r$ 作中间投入的交易矩阵；$A^{sr}=Z^{sr}\mathrm{diag}(X^r)^{-1}$ 为对应的直接投入系数矩阵；$X^r$ 是 $r$ 的总产出向量。
- $A$ 为全球直接投入系数矩阵，$B=(I-A)^{-1}$ 为全球 Leontief 逆矩阵，$B^{sr}$ 是其中的 $s,r$ 分块；$L^{ss}=(I-A^{ss})^{-1}$ 为 $s$ 的国内 Leontief 逆矩阵。
- $V^s=(v_1^s,\ldots,v_N^s)$ 为行向量，其中 $v_k^s=VA_k^s/X_k^s$；$Y^{sr}$ 是 $s$ 生产、由 $r$ 最终使用的产品向量，已合并最终需求类别。
- $E^{sr}=A^{sr}X^r+Y^{sr}$ 为 $s$ 到 $r$ 的逐产业总出口；$E^{r\ast}=\sum_{u\ne r}(A^{ru}X^u+Y^{ru})$ 为 $r$ 向世界其他经济体的逐产业出口。
- $Q^{sr}=\sum_{t\notin\{s,r\}}V^tB^{ts}$ 表示第三方经济体增加值进入 $s$ 生产的单位产品的贡献系数。${}^{\mathsf{T}}$ 表示转置，$\odot$ 表示逐元素相乘（对应 MATLAB 的 `.*`）。

上述向量在公式中按**出口产品所属产业**排列。因此，$V^sB^{ss}$ 含有来自 $s$ 内其他上游产业的增加值贡献，不能将 $T_1$ 解释为出口行业自身创造的增加值。

### 国内增加值在国外吸收：T1–T5

**T1 — DVA_FIN：最终产品出口中的国内增加值。** 出口国直接向进口国提供最终产品，其中来源于出口国的增加值。

```math
T_1^{sr}=(V^sB^{ss})^{\mathsf{T}}\odot Y^{sr}.
```

**T2 — DVA_INT：中间品出口经直接进口国生产并在当地最终吸收的国内增加值。**

```math
T_2^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot(A^{sr}B^{rr}Y^{rr}).
```

**T3 — DVA_INTrex1：中间品经直接进口国再出口至第三国，最终由第三国本地吸收的国内增加值。** 这里追踪的是第三国生产供其本国最终使用的产品。

```math
T_3^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{tt}\right).
```

**T4 — DVA_INTrex2：中间品经直接进口国加工为最终产品并出口至第三国的国内增加值。**

```math
T_4^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}B^{rr}\sum_{u\notin\{s,r\}}Y^{ru}\right).
```

**T5 — DVA_INTrex3：中间品经直接进口国再出口为中间品，并通过第三国后续生产用于国外最终需求的国内增加值。**

```math
T_5^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}
\sum_{u\notin\{s,t\}}Y^{tu}\right).
```

### 出口后返回本国的国内增加值：T6–T8

**T6 — RDV_FIN1：经直接进口国制成最终产品后回流的国内增加值。** 最终产品由 $r$ 出口回 $s$，并在 $s$ 使用。

```math
T_6^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot(A^{sr}B^{rr}Y^{rs}).
```

**T7 — RDV_FIN2：经第三国制成最终产品后回流的国内增加值。**

```math
T_7^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{ts}\right).
```

**T8 — RDV_INT：以中间品形式回流，并用于本国最终产品生产和消费的国内增加值。**

```math
T_8^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot(A^{sr}B^{rs}Y^{ss}).
```

### 国内增加值的重复计算：T9–T10

**T9 — DDC_FIN：与最终产品出口生产相关的国内重复计算项。** 这部分记录了跨境中间品往返带来的重复计价，不是新增创造的增加值。

```math
T_9^{sr}=(V^sL^{ss})^{\mathsf{T}}\odot
\left(A^{sr}B^{rs}\sum_{u\ne s}Y^{su}\right).
```

**T10 — DDC_INT：与中间品出口相关的国内重复计算项。**

```math
T_{10}^{sr}=\left(V^sB^{ss}-V^sL^{ss}\right)^{\mathsf{T}}
\odot(A^{sr}X^r).
```

### 直接进口国的增加值及重复计算：T11–T13

**T11 — MVA_FIN：出口国最终产品出口中来自直接进口国的增加值。**

```math
T_{11}^{sr}=(V^rB^{rs})^{\mathsf{T}}\odot Y^{sr}.
```

**T12 — MVA_INT：出口国中间品出口中来自直接进口国的增加值。**

```math
T_{12}^{sr}=(V^rB^{rs})^{\mathsf{T}}\odot
(A^{sr}L^{rr}Y^{rr}).
```

**T13 — MDC：来自直接进口国的增加值在出口生产中形成的重复计算项。**

```math
T_{13}^{sr}=(V^rB^{rs})^{\mathsf{T}}\odot
(A^{sr}L^{rr}E^{r\ast}).
```

### 第三方经济体的增加值及重复计算：T14–T16

**T14 — OVA_FIN：出口国最终产品出口中来自第三方经济体的增加值。**

```math
T_{14}^{sr}=(Q^{sr})^{\mathsf{T}}\odot Y^{sr}.
```

**T15 — OVA_INT：出口国中间品出口中来自第三方经济体的增加值。**

```math
T_{15}^{sr}=(Q^{sr})^{\mathsf{T}}\odot
(A^{sr}L^{rr}Y^{rr}).
```

**T16 — ODC：来自第三方经济体的增加值在出口生产中形成的重复计算项。**

```math
T_{16}^{sr}=(Q^{sr})^{\mathsf{T}}\odot
(A^{sr}L^{rr}E^{r\ast}).
```

### 合计关系

对给定的 $s\ne r$ 和出口产业，16 项必须恢复该产业对 $r$ 的总出口：

```math
E^{sr}=\sum_{k=1}^{16}T_k^{sr}.
```

按照附录 E 的经济分类，国内增加值在国外吸收为 $T_1+\cdots+T_5$；返回本国的国内增加值为 $T_6+T_7+T_8$；国内重复计算为 $T_9+T_{10}$；外国增加值为 $T_{11}+T_{12}+T_{14}+T_{15}$；外国重复计算为 $T_{13}+T_{16}$。其中，$T_{11}$、$T_{12}$、$T_{13}$ 来自直接进口国，$T_{14}$、$T_{15}$、$T_{16}$ 来自第三方经济体。不能把重复计算项当作新的增加值，也不能直接把各项的比例作不加权平均。

公式按 `valueadded2007.m` 的 16 项向量实现及原论文 Table E1 整理。详情见 [Wang、Wei 和 Zhu（2013），NBER Working Paper 19677](https://www.nber.org/papers/w19677) 的式（18）与附录 E。原程序中的 `tt2`–`tt9` 为 T2–T9 中间品出口路径的辅助变量，不是另一套分解项。

## 验证与研究Cons

在 2007 年原表上重新运行 Python，逐项与 16 份已存 MATLAB CSV 对照。最大逐项缩放误差为 0.004986%（分母为参考值绝对值和 1 中较大者）；逐行业双边出口恒等式最大绝对残差为 1.1642 × 10⁻¹⁰ 百万美元。这里没有重新运行 MATLAB。完整 OECD 年度表尚未做同等规模的验证；完整 TiVA 与中国区域表链接也不在此移植范围。保留的老版 Streamlit 入口是可选组件，不是本版双语桌面软件。

数值验证：`python -m pip install -e '.[dev]'`，然后 `python -m pytest -q`。本地重新生成离线页：`python build_offline_preview.py`。字号和导出检查见 `reports/figure_qa.json`。未替原始数据或 MATLAB 程序授予新的再分发许可。

## 方法引用

如果在论文或研究项目中使用这里实现的 WWZ 分解方法，请引用其原始研究：

Wang, Z., Wei, S. J., & Zhu, K. (2013). *Quantifying international production sharing at the bilateral and sector levels* (No. w19677). National Bureau of Economic Research.

[NBER Working Paper 19677](https://www.nber.org/papers/w19677)

项目维护：**[Jiacheng Zheng](https://karcen.github.io/)**。
