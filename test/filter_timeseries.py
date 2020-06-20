import pandas as pd

import sys
sys.path.append('../../connectTCR')
from connectTCR.io import *
from connectTCR.signal import *

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
sns.set_context("paper")
rcParams['figure.dpi'] = 300
rcParams['savefig.transparent'] = True
rcParams['savefig.dpi'] = 300

outdir = '../output/timeseries/'
# savename = 'csf'
# files = [outdir+savename+ext for ext in ['.npz', '.columns', '.index']]
# df = read_npz(*files)
# meta = pd.read_csv(outdir+'csf.meta.csv', index_col='TRB')
# df = pd.concat([df, meta], axis=1, sort=False)
# print(df.head())

df, timepoints = read_timeseries(outdir, 'csf')
# remove TRB with zero frquencies at all timepoints
df = df.loc[df[timepoints].sum(axis=1) > 0]
# convert to tidy format
df_tidy = pd.melt(df.reset_index(), 
    id_vars=['TRB'] + [x for x in df.columns if x not in timepoints], 
    var_name='Timepoint', value_name='Frequency')

# rank per timepoint
rank =  rank_columns(df, timepoints)
rank.index.name = 'TRB'
rank_tidy = pd.melt(rank.reset_index(), 
    id_vars=['TRB'], 
    var_name='Timepoint', value_name='Rank')

# filter by mode
mask = filter_columns(df, 'mode', timepoints)
mask.index.name = 'TRB'
mask_tidy = pd.melt(mask.reset_index(), 
    id_vars=['TRB'], 
    var_name='Timepoint', value_name='Filter')

merge_tidy = merge_dfs([df_tidy, mask_tidy, rank_tidy], ['TRB', 'Timepoint'])
g = sns.FacetGrid(merge_tidy, col='Timepoint', col_wrap=6, 
    hue='Filter', palette={False:'grey', True:'r'},
    height=1.5, aspect=1, ylim=(-0.001, 0.02))
g.map(plt.scatter, "Rank", "Frequency", alpha=.7, s=5)
g.set_titles("{col_name}")
g.fig.tight_layout()
g.add_legend()
g.savefig(outdir+"csf_filter_mode.png")
# mask.to_csv(outdir+"csf_filter_mode_mask.csv", index=True)

# nnz_mask_tidy = mask_tidy.dropna()
# trbs = nnz_mask_tidy.loc[nnz_mask_tidy['Filter'], 'TRB'].unique()
# with open(outdir+"csf_filter_mode.txt", "w") as f:
#     for tcr in trbs:
#         f.write(tcr+'\n')

df, timepoints = read_timeseries(outdir, 'pb')
# remove TRB with zero frquencies at all timepoints
df = df.loc[df[timepoints].sum(axis=1) > 0]
# convert to tidy format
df_tidy = pd.melt(df.reset_index(), 
    id_vars=['TRB'] + [x for x in df.columns if x not in timepoints], 
    var_name='Timepoint', value_name='Frequency')
# rank per timepoint
rank =  rank_columns(df, timepoints)
rank.index.name = 'TRB'
rank_tidy = pd.melt(rank.reset_index(), 
    id_vars=['TRB'], 
    var_name='Timepoint', value_name='Rank')
merge_tidy = merge_dfs([df_tidy, rank_tidy], ['TRB', 'Timepoint'])
# g = sns.FacetGrid(merge_tidy, col='Timepoint', col_wrap=4, 
#     hue='Signal/Noise', palette={'Noise':'grey', 'Signal':'r'},
#     height=1.5, aspect=1, sharey=True, ylim=(-0.001, 0.01))
# g.map(plt.scatter, "Rank", "Frequency", alpha=.7, s=5)
# g.set_titles("{col_name}")
# g.fig.tight_layout()
# g.add_legend()
# g.savefig(outdir+"pb_filter.png")


"""
# filter by percentile, max method
mask = filter_columns(df, 'percentile', timepoints, pct=0.99, method='max')
mask.index.name = 'TRB'
mask_tidy = pd.melt(mask.reset_index(), 
    id_vars=['TRB'], 
    var_name='Timepoint', value_name='Filter')

merge_tidy = merge_dfs([df_tidy, mask_tidy, rank_tidy], ['TRB', 'Timepoint'])
g = sns.FacetGrid(merge_tidy, col='Timepoint', col_wrap=3, 
    hue='Filter', palette={False:'grey', True:'r'},
    height=2, aspect=1.5, ylim=(0, 0.02))
g.map(plt.scatter, "Rank", "Frequency", alpha=.7, s=5)
g.add_legend()
g.savefig("../output/filter_pct_max_0.99.png")

# filter by percentile, min method
mask = filter_columns(df, 'percentile', timepoints, pct=0.99, method='min')
mask.index.name = 'TRB'
mask_tidy = pd.melt(mask.reset_index(), 
    id_vars=['TRB'], 
    var_name='Timepoint', value_name='Filter')

merge_tidy = merge_dfs([df_tidy, mask_tidy, rank_tidy], ['TRB', 'Timepoint'])
g = sns.FacetGrid(merge_tidy, col='Timepoint', col_wrap=3, 
    hue='Filter', palette={False:'grey', True:'r'},
    height=2, aspect=1.5, ylim=(0, 0.02))
g.map(plt.scatter, "Rank", "Frequency", alpha=.7, s=5)
g.add_legend()
g.savefig("../output/filter_pct_min_0.99.png")

# filter by percentile, first method
mask = filter_columns(df, 'percentile', timepoints, pct=0.99, method='first')
mask.index.name = 'TRB'
mask_tidy = pd.melt(mask.reset_index(), 
    id_vars=['TRB'], 
    var_name='Timepoint', value_name='Filter')

merge_tidy = merge_dfs([df_tidy, mask_tidy, rank_tidy], ['TRB', 'Timepoint'])
g = sns.FacetGrid(merge_tidy, col='Timepoint', col_wrap=3, 
    hue='Filter', palette={False:'grey', True:'r'},
    height=2, aspect=1.5, ylim=(0, 0.02))
g.map(plt.scatter, "Rank", "Frequency", alpha=.7, s=5)
g.add_legend()
g.savefig("../output/filter_pct_first_0.99.png")


"""