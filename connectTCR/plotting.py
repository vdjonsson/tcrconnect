import seaborn as sns
from matplotlib import rcParams
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex, to_rgba

def set_figure_params(context='paper'):
    rcParams["figure.dpi"] = 300
    rcParams["savefig.transparent"] = True
    rcParams["savefig.dpi"] = 300
    sns.set_context(context)
    return

def barplot(mat, palette, normalize=True, figsize=(2,2), stacked=True, ylabel=None, \
    outdir='./', save=None, ylog=False, width=1, **kwargs):
    
    with sns.axes_style('ticks'):
        fig, ax = plt.subplots(figsize=figsize)
        if normalize:
            prop = mat.apply(lambda x: x / x.sum(), axis=1)
        else:
            prop = mat
        prop.plot(ax=ax, kind='bar', stacked=stacked, \
            color=[palette[c] for c in mat.columns], width=1, **kwargs)
        plt.legend(bbox_to_anchor=(1,1))
        plt.ylabel(ylabel)
        if ylog:
            ax.set_yscale("log")
        sns.despine()
        if save is not None:
            plt.savefig(outdir+save+'.png', transparent=True, bbox_inches='tight')
    return
