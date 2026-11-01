# GVC Explorer

[English](README_EN.md) · [Jiacheng Zheng](https://karcen.github.io/)

GVC Explorer 将 `valueadded2007.m` 中的全球价值链出口 16 项分解（T1–T16）迁移到了 Python。项目保留了原始 MATLAB 脚本、2007 年投入产出表和历史计算结果，方便检查公式、比较数值和追溯数据来源。计算引擎与界面分开：Streamlit 用于加载和计算投入产出表；`offline_dashboard.html` 用于浏览已经计算好的 2007 年结果。

目前完成的是原 MATLAB 程序中的双边、产业层级 16 项分解。完整 TiVA 程序和中国区域表链接程序尚未迁移。

## 快速使用

不安装 Python 也可以直接打开 `offline_dashboard.html`。网页提供出口经济体、进口经济体、产业和分解项筛选，显示 16 项贡献、目的地热力图与出口目的地排序。点击热力图单元格会同步更新选择。网页右上角可切换浅色／深色模式；浏览器允许本地存储时，会记住上次的选择。该网页只展示内置的 2007 年结果，不能计算新文件。

需要重新核算时，在项目目录下运行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
streamlit run app.py
```

在 Streamlit 中选择“内置 2007 样例”，点击“载入并计算”。也可以指定本地 IO 文件夹，或上传包含完整输入文件的 ZIP。Python 版本要求见 `pyproject.toml`（目前为 3.10 及以上）。

如果不需要图形界面，可运行：

```bash
python run_batch.py --input data/reference_2007 --output output
```

命令行结果保存在 `output/wwz_results.npz` 和 `output/validation.json`。其中 `terms` 的形状为 `(16, S×N, S)`，`total_exports` 和 `discrepancy` 的形状为 `(S×N, S)`。`S` 是经济体数，`N` 是每个经济体的产业数。

## 数据输入

目前可直接读取两种已定义的布局。

一是历史样例格式：文件名为 `2007global.xlsx`，工作表为 `Sheet2`，行列布局须与原 MATLAB 脚本一致。

二是标准 CSV 文件夹，必须同时包含以下四个文件：

| 文件 | 内容 | 形状 |
| --- | --- | --- |
| `Z.csv` | 中间投入矩阵 | `(S×N, S×N)` |
| `Y.csv` | 按目的地经济体汇总后的最终需求 | `(S×N, S)` |
| `VA.csv` | 增加值向量 | `(S×N,)` |
| `X.csv` | 总产出向量 | `(S×N,)` |

矩阵必须按“经济体 → 产业”的顺序排列。所有国家的产业数须一致；同一套经济体和产业顺序必须贯穿 `Z`、`Y`、`VA` 和 `X`。`Y` 已按目的地合并最终需求类别，不能把带有未合并需求类别的原始矩阵直接放入此接口。

可在输入文件夹添加 `metadata.json`，注明 `year`、`unit`、`country_names`、`industry_names`。名称数组长度必须与实际维度匹配。没有经过确认的名称时，系统显示编号，不会根据位置猜测国家和产业。

示例文件位于 `examples/`。当前并不支持任意格式的 OECD 或 WIOD 原始 Excel 表直接拖入后自动推断全部经济变量；这些数据需要先转换成上述布局。

## OECD ICIO 2025 Extended 名称字典

`data/oecd_source/ReadMe_ICIO_extended.xlsx` 是本项目经济体和产业名称的来源。已从其中核对 85 个地区／经济体代码、50 个产业代码与 ISIC Rev.4 对应关系，并检查 `RowItems`、`ColItems` 的 4,250 个产业位置。字典位于 `data/catalog/` 和 `src/gvc/data/oecd_icio_2025_extended.json`。

Streamlit 页面提供可检索的 OECD 代码目录；离线网页也提供单独的 OECD 地区和产业选择器。这些选择器仅供查阅名称，不会改变 2007 年计算结果。

**2007 年原始样例采用 48 个经济体／地区、17 个产业。** 该数据的权威名称顺序目前没有得到确认，因此不能套用 OECD 2025 的 85×50 名称。对于真实的 OECD 2025 Extended 输入，必须核对行列顺序，并依据 `examples/oecd_icio_2025_metadata_template.json` 提供分类代码和确认标志。操作细节见 `docs/oecd_icio_label_mapping.md`。

OECD README 仅提供代码表，不包含完整的 2025 年投入产出数值矩阵；项目尚未完成 85×50 规模的数值复现与性能验收。

## WWZ 16 项分解：公式与经济含义

以下采用原 MATLAB 程序 `valueadded2007.m` 中的 T1–T16 顺序，与 Wang、Wei 和 Zhu（2013）附录 E 的 Table E1 一一对应。分解对象是出口经济体 $s$ 向进口经济体 $r$ 的**逐产业总出口向量**，而非某个产业创造的全部增加值。16 个分量均为 $N\times1$ 向量；选定产业后，Dashboard 显示相应的标量。

### 记号

- $s$ 为出口经济体，$r$ 为直接进口经济体，$t,u$ 为用于追踪后续生产或最终吸收的其他经济体，且 $s\ne r$；$N$ 为每个经济体的产业数。
- $Z^{sr}$ 为 $s$ 的产品供给 $r$ 作中间投入的交易矩阵；$A^{sr}=Z^{sr}\operatorname{diag}(X^r)^{-1}$ 为对应的直接投入系数矩阵；$X^r$ 是 $r$ 的总产出向量。
- $A$ 为全球直接投入系数矩阵，$B=(I-A)^{-1}$ 为全球 Leontief 逆矩阵，$B^{sr}$ 是其中的 $s,r$ 分块；$L^{ss}=(I-A^{ss})^{-1}$ 为 $s$ 的国内 Leontief 逆矩阵。
- $V^s=(v_1^s,\ldots,v_N^s)$ 为行向量，其中 $v_k^s=VA_k^s/X_k^s$；$Y^{sr}$ 是 $s$ 生产、由 $r$ 最终使用的产品向量，已合并最终需求类别。
- $E^{sr}=A^{sr}X^r+Y^{sr}$ 为 $s$ 到 $r$ 的逐产业总出口；$E^{r*}=\sum_{u\ne r}(A^{ru}X^u+Y^{ru})$ 为 $r$ 向世界其他经济体的逐产业出口。
- $Q^{sr}=\sum_{t\notin\{s,r\}}V^tB^{ts}$ 表示第三方经济体增加值进入 $s$ 生产的单位产品的贡献系数。${}^{\mathsf T}$ 表示转置，$\odot$ 表示逐元素相乘（对应 MATLAB 的 `.*`）。

上述向量在公式中按**出口产品所属产业**排列。因此，$V^sB^{ss}$ 含有来自 $s$ 内其他上游产业的增加值贡献，不能将 $T_1$ 解释为出口行业自身创造的增加值。

### 国内增加值在国外吸收：T1–T5

**T1 — DVA_FIN：最终产品出口中的国内增加值。** 出口国直接向进口国提供最终产品，其中来源于出口国的增加值。

$$
T_1^{sr}=(V^sB^{ss})^{\mathsf T}\odot Y^{sr}.
$$

**T2 — DVA_INT：中间品出口经直接进口国生产并在当地最终吸收的国内增加值。**

$$
T_2^{sr}=(V^sL^{ss})^{\mathsf T}\odot(A^{sr}B^{rr}Y^{rr}).
$$

**T3 — DVA_INTrex1：中间品经直接进口国再出口至第三国，最终由第三国本地吸收的国内增加值。** 这里追踪的是第三国生产供其本国最终使用的产品。

$$
T_3^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{tt}\right).
$$

**T4 — DVA_INTrex2：中间品经直接进口国加工为最终产品并出口至第三国的国内增加值。**

$$
T_4^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}B^{rr}\sum_{u\notin\{s,r\}}Y^{ru}\right).
$$

**T5 — DVA_INTrex3：中间品经直接进口国再出口为中间品，并通过第三国后续生产用于国外最终需求的国内增加值。**

$$
T_5^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}
\sum_{u\notin\{s,t\}}Y^{tu}\right).
$$

### 出口后返回本国的国内增加值：T6–T8

**T6 — RDV_FIN1：经直接进口国制成最终产品后回流的国内增加值。** 最终产品由 $r$ 出口回 $s$，并在 $s$ 使用。

$$
T_6^{sr}=(V^sL^{ss})^{\mathsf T}\odot(A^{sr}B^{rr}Y^{rs}).
$$

**T7 — RDV_FIN2：经第三国制成最终产品后回流的国内增加值。**

$$
T_7^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}\sum_{t\notin\{s,r\}}B^{rt}Y^{ts}\right).
$$

**T8 — RDV_INT：以中间品形式回流，并用于本国最终产品生产和消费的国内增加值。**

$$
T_8^{sr}=(V^sL^{ss})^{\mathsf T}\odot(A^{sr}B^{rs}Y^{ss}).
$$

### 国内增加值的重复计算：T9–T10

**T9 — DDC_FIN：与最终产品出口生产相关的国内重复计算项。** 这部分记录了跨境中间品往返带来的重复计价，不是新增创造的增加值。

$$
T_9^{sr}=(V^sL^{ss})^{\mathsf T}\odot
\left(A^{sr}B^{rs}\sum_{u\ne s}Y^{su}\right).
$$

**T10 — DDC_INT：与中间品出口相关的国内重复计算项。**

$$
T_{10}^{sr}=\left(V^sB^{ss}-V^sL^{ss}\right)^{\mathsf T}
\odot(A^{sr}X^r).
$$

### 直接进口国的增加值及重复计算：T11–T13

**T11 — MVA_FIN：出口国最终产品出口中来自直接进口国的增加值。**

$$
T_{11}^{sr}=(V^rB^{rs})^{\mathsf T}\odot Y^{sr}.
$$

**T12 — MVA_INT：出口国中间品出口中来自直接进口国的增加值。**

$$
T_{12}^{sr}=(V^rB^{rs})^{\mathsf T}\odot
(A^{sr}L^{rr}Y^{rr}).
$$

**T13 — MDC：来自直接进口国的增加值在出口生产中形成的重复计算项。**

$$
T_{13}^{sr}=(V^rB^{rs})^{\mathsf T}\odot
(A^{sr}L^{rr}E^{r*}).
$$

### 第三方经济体的增加值及重复计算：T14–T16

**T14 — OVA_FIN：出口国最终产品出口中来自第三方经济体的增加值。**

$$
T_{14}^{sr}=(Q^{sr})^{\mathsf T}\odot Y^{sr}.
$$

**T15 — OVA_INT：出口国中间品出口中来自第三方经济体的增加值。**

$$
T_{15}^{sr}=(Q^{sr})^{\mathsf T}\odot
(A^{sr}L^{rr}Y^{rr}).
$$

**T16 — ODC：来自第三方经济体的增加值在出口生产中形成的重复计算项。**

$$
T_{16}^{sr}=(Q^{sr})^{\mathsf T}\odot
(A^{sr}L^{rr}E^{r*}).
$$

### 合计关系

对给定的 $s\ne r$ 和出口产业，16 项必须恢复该产业对 $r$ 的总出口：

$$
E^{sr}=\sum_{k=1}^{16}T_k^{sr}.
$$

按照附录 E 的经济分类，国内增加值在国外吸收为 $T_1+\cdots+T_5$；返回本国的国内增加值为 $T_6+T_7+T_8$；国内重复计算为 $T_9+T_{10}$；外国增加值为 $T_{11}+T_{12}+T_{14}+T_{15}$；外国重复计算为 $T_{13}+T_{16}$。其中，$T_{11}$、$T_{12}$、$T_{13}$ 来自直接进口国，$T_{14}$、$T_{15}$、$T_{16}$ 来自第三方经济体。不能把重复计算项当作新的增加值，也不能直接把各项的比例作不加权平均。

公式按 `valueadded2007.m` 的 16 项向量实现及原论文 Table E1 整理。详情见 [Wang、Wei 和 Zhu（2013），NBER Working Paper 19677](https://www.nber.org/papers/w19677) 的式（18）与附录 E。原程序中的 `tt2`–`tt9` 为 T2–T9 中间品出口路径的辅助变量，不是另一套分解项。

## 核算与验证

计算入口在 `src/gvc/engine.py`。该模块逐式移植 `valueadded2007.m` 中的 T1–T16 及相关中间品出口计算；投入产出读取位于 `src/gvc/loaders.py`。Leontief 线性系统使用 SciPy 求解。

已使用原始 2007 年工作簿执行 Python 核算，并对照原始文件夹保存的 16 个 MATLAB CSV 结果：

- 样本维度：48 个经济体／地区、每个 17 个产业。
- 16 项结果：`(16, 816, 48)`。
- 与历史 CSV 的最大缩放相对误差：小于 0.005%，分母为 `max(|CSV 参考值|, 1)`。
- 16 项合计与双边产业总出口之间的最大绝对残差：约 `1.16×10⁻¹⁰`，单位沿用原始工作簿。

逐项误差见 `reports/validation_2007.json`。历史 CSV 的有限输出精度会影响逐元素比较。原 MATLAB 程序未在本环境重新运行，因此这项检查是对**既有 MATLAB 导出结果**的复现，而非重新执行 MATLAB 后的双环境测试。其他年份、其他数据布局和 OECD 2025 全量表尚无相同程度的验证。

开发测试使用：

```bash
python -m pytest -q
```

## 项目文件

| 路径 | 用途 |
| --- | --- |
| `app.py` | Streamlit 计算界面与图表 |
| `offline_dashboard.html` | 离线浏览 2007 年计算结果，支持深浅主题 |
| `build_offline_preview.py` | 根据已有结果重新生成离线网页 |
| `src/gvc/engine.py` | 16 项分解计算 |
| `src/gvc/loaders.py` | IO 数据读取 |
| `src/gvc/metadata.py` | 产业和经济体名称校验 |
| `data/reference_2007/` | 2007 年样例和历史 CSV |
| `data/matlab_original/` | 原始 MATLAB 文件 |
| `data/catalog/` | OECD 2025 Extended 标签表 |
| `reports/` | 核算验证记录与图件 |
| `tests/` | Python 测试 |

重新生成离线页面可在完成安装后运行：

```bash
python build_offline_preview.py
```

该命令读取项目中已经计算好的 `output/wwz_python_2007.npz`，不会重新执行 WWZ 分解。

## 现有边界

`tradeinvalueadded2007.m`、`GVCDVC.m` 和区域表链接工作簿保留在项目中，但没有完成 Python 移植。T1–T16 的界面分组用于导航，不能代替论文中的正式经济定义。只有一个经过复现的 2007 年样例，不能据此生成跨期趋势；该样例的货币单位也尚未从原始表格中独立确认。

离线网页曾通过 Chromium 交互检查；Streamlit 本地服务器仍需在安装依赖后做完整端到端验收。图形导出由 Matplotlib 实现，尚未经过用户本地 Nature Figure Skill 的完整审查。

计算数据留在本地，不通过应用上传至外部服务。公开 GitHub 仓库前，请单独确认原 MATLAB 程序和原始 IO 数据的再分发许可；`.gitignore` 已将相关原始材料排除在默认提交范围之外。`AGENTS.md` 与 `docs/CODEX_HANDOFF.md` 记录后续 Codex 开发所需的信息，不代表本项目已由 Codex 执行。

## 方法引用

如果在论文或研究项目中使用这里实现的 WWZ 分解方法，请引用其原始研究：

Wang, Z., Wei, S. J., & Zhu, K. (2013). *Quantifying international production sharing at the bilateral and sector levels* (No. w19677). National Bureau of Economic Research.

[NBER Working Paper 19677](https://www.nber.org/papers/w19677)

项目维护：**[Jiacheng Zheng](https://karcen.github.io/)**。
