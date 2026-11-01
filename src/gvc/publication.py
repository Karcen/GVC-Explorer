"""Static research figure export, output SVG/PDF/PNG."""
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

_PALETTE={'直接最终产品':'#194568','本国增加值（中间投入路径）':'#467d9a',
          '本国重复核算':'#8b9d9f','进口方来源':'#c58a47','其他经济体来源':'#916657'}

def bar_figure(df,title):
    fig,ax=plt.subplots(figsize=(8,6),layout='constrained')
    ys=np.arange(len(df))
    vals=df['value'].to_numpy(dtype=float)
    colors=[_PALETTE[g] for g in df['group']]
    ax.barh(ys,vals,color=colors,height=0.72)
    ax.set_yticks(ys,df['term'])
    ax.invert_yaxis()
    ax.axvline(0,linewidth=0.8,color='#30363b')
    ax.set_title(title,pad=15,fontsize=12,loc='left')
    ax.set_xlabel('Decomposition value (source unit)')
    ax.spines[['top','right','left']].set_visible(False)
    ax.grid(axis='x',alpha=0.2)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(mticker.EngFormatter())
    return fig
