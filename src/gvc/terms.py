"""Research dictionary with labels derived from valueadded2007.m, not canonical WWZ titles.

Formula is transcribed from the original MATLAB program in compact notation.
The symbol ⊙ represents elementwise multiplication by source-industry.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class TermInfo:
    key: str
    label_zh: str
    formula: str
    source_lines: str

TERMS=[
    TermInfo('T1','出口最终产品的本国增加值','(v_i B_ii)^T ⊙ Y_ij','281–292'),
    TermInfo('T2','中间投入出口路径 tt2：由进口国本地最终需求引致','(v_i L_i)^T ⊙ tt2_ij','295–306'),
    TermInfo('T3','中间投入出口路径 tt3：第三地本地最终需求','(v_i L_i)^T ⊙ tt3_ij','308–319'),
    TermInfo('T4','中间投入出口路径 tt4：进口国最终产品再出口','(v_i L_i)^T ⊙ tt4_ij','321–332'),
    TermInfo('T5','中间投入出口路径 tt5：第三地生产及最终需求','(v_i L_i)^T ⊙ tt5_ij','335–346'),
    TermInfo('T6','中间投入出口路径 tt6：经进口国返回出口国最终需求','(v_i L_i)^T ⊙ tt6_ij','348–359'),
    TermInfo('T7','中间投入出口路径 tt7：跨国生产后返回出口国最终需求','(v_i L_i)^T ⊙ tt7_ij','363–374'),
    TermInfo('T8','中间投入出口路径 tt8：出口国本地最终需求','(v_i L_i)^T ⊙ tt8_ij','377–388'),
    TermInfo('T9','中间投入出口路径 tt9：出口国对外最终需求','(v_i L_i)^T ⊙ tt9_ij','391–402'),
    TermInfo('T10','本国价值来源的全球逆矩阵与局部逆矩阵差额','[v_i (B_ii − L_i)]^T ⊙ DEI_ij','406–417'),
    TermInfo('T11','直接进口国价值来源：最终产品出口','(v_j B_ji)^T ⊙ Y_ij','420–431'),
    TermInfo('T12','直接进口国价值来源：中间投入流向其本地最终需求','(v_j B_ji)^T ⊙ (A_ij L_j Y_jj)','435–446'),
    TermInfo('T13','直接进口国价值来源：中间投入流向其对外出口','(v_j B_ji)^T ⊙ (A_ij L_j TE_j)','449–460'),
    TermInfo('T14','其他经济体价值来源：最终产品出口','w_ij^T ⊙ Y_ij','480–491'),
    TermInfo('T15','其他经济体价值来源：中间投入流向进口国本地最终需求','w_ij^T ⊙ (A_ij L_j Y_jj)','494–505'),
    TermInfo('T16','其他经济体价值来源：中间投入流向进口国对外出口','w_ij^T ⊙ (A_ij L_j TE_j)','508–519')
]
# w_ij = sum_{t ≠ i,j} v_t B_ti; T11..T16 are algebraic source-value terms,
# not a stand-alone physical chain-flow model.
