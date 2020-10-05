import os
import numpy as np
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

def barplot(mat, palette, normalize=True, ax=None,  figsize=(2,2), stacked=True, ylabel=None, \
    outdir='./', save=None, ylog=False, width=1, xlim=None,**kwargs):
    
    with sns.axes_style('ticks'):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        if normalize:
            prop = mat.apply(lambda x: x / x.sum(), axis=1)
        else:
            prop = mat
        prop.plot(ax=ax, kind='bar', stacked=stacked, \
            color=[palette[c] for c in mat.columns], width=width, **kwargs)
        plt.legend(bbox_to_anchor=(1,1))
        plt.ylabel(ylabel)
        sns.despine()
        if xlim is not None:
            ax.set_xlim(*xlim)
        if ylog:
            ax.set_yscale("log")
        if save is not None:
            plt.savefig(outdir+save+'.png', transparent=True, bbox_inches='tight')
    return

def label(x, color, label, **kwargs):
    data = kwargs.pop('data')
    label_format = kwargs.pop('label_format')
    ha = kwargs.pop('ha')
    new_color = kwargs.pop('new_color')
    if new_color is not None:
        color = new_color
    ax = plt.gca()
    ax.text(0, .2, label_format.format(data[x].values[0]), 
            fontweight="bold", color=color,
            ha=ha, va="center", transform=ax.transAxes)

def overlapping_kde(df, key, row, hue, 
    outdir, savename, hist=False, kde=True, label_format="{}", label_ha="left", label_color=None, 
    height=0.5, aspect=6, sharey=True, hspace=-0.25, **kwargs):

    with sns.axes_style(style='white', rc={"axes.facecolor": (0, 0, 0, 0)}):
        g = sns.FacetGrid(df, row=row, hue=hue, 
            height=height, aspect=aspect, sharey=sharey, **kwargs)
        bins = np.arange(0, df[key].values.max()+1, 1)
        #g = g.map(plt.hist, 0, bins=bins, norm=True)
        if hist:
            g.map(plt.hist, key, bins=bins, density=True)
        if kde:
            g.map(sns.kdeplot, key, clip_on=False, shade=True, alpha=1, lw=1.5, bw=1)
            g.map(sns.kdeplot, key, clip_on=False, color="w", lw=2, bw=1)
        g.map(plt.axhline, y=0, lw=2, clip_on=False)

        g.map_dataframe(label, row, label_format=label_format, ha=label_ha, 
            new_color=label_color)
        g.fig.suptitle(row)
        g.set_titles("")
        g.set_xlabels(key)
        g.add_legend()
        g.fig.subplots_adjust(hspace=hspace)
        g.set(yticks=[])
        g.despine(bottom=True, left=True)
        g.savefig(
            os.path.join(outdir, '_'.join([savename, key, row, hue])+'.png')
        )
    return g

def get_loglim(data, pct=0.05):
    vmin = data.min()
    vmax = data.max()
    vrange = np.array([vmin, vmax])
    logvrange = np.log10(vrange)
    interval = logvrange[1] - logvrange[0]
    margin = interval * pct
    logvrange += [-margin, margin]
    return 10**logvrange
