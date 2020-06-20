import pandas as pd

import sys
sys.path.append('../../connectTCR')
from connectTCR.io import *
from connectTCR.signal import *

import seaborn as sns
import matplotlib.pyplot as plt

outdir = '../output/timeseries/'

df_csf, t_csf = read_timeseries(outdir, 'csf', meta_ext='.meta.v3.csv')
df_csf_tidy = tidy_timeseries(df_csf)
print(df_csf_tidy.head())

test = df_csf_tidy.loc[df_csf_tidy.kmeans.isin(['1','2'])]
print(test.shape)
signal_tidy = df_csf_tidy.loc[df_csf_tidy.frequency_type=='signal']
g = sns.FacetGrid(signal_tidy, col='kmeans', col_wrap=4, 
    hue='kshape',
    height=2, aspect=1.5, sharey=False, )


def plot_units(x, y, color, **kwargs):
    if 'label' in kwargs:
        label = kwargs.pop('label')
    data = kwargs.pop('data') 
    units = kwargs.pop('units')
    if 'new_color' in kwargs:
        color = kwargs.pop('new_color')
    for unit in data[units].unique():
        inds = data[units]==unit
        plt.plot(data.loc[inds, x], data.loc[inds, y], '-', color=color, **kwargs)

g.map_dataframe(plot_units, "Timepoint", "Frequency", units='TRB', alpha=0.1, new_color='grey')
g.map(sns.lineplot, "Timepoint", "Frequency", alpha=1)
g.add_legend()
for ax in g.axes.ravel():
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
g.savefig(outdir+"csf_kmeans.png")

nnz = signal_tidy.loc[signal_tidy['Frequency']!=0]
# df_pb, t_pb = read_timeseries(outdir, 'pb')
# df_pb = df_pb.reset_index()
