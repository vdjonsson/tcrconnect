import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import sys
sys.path.append('../../connectTCR')
from connectTCR.io import *
from connectTCR.signal import *
from connectTCR.utils import *

from connectTCR.mapping import map_overlap
from connectTCR.pipeline import plot_connection

import figure_settings
tsdir = '../output/timeseries/'

df_csf, t_csf = read_timeseries(tsdir, 'csf', meta_ext='.meta.v3.csv')
df_pb, t_pb = read_timeseries(tsdir, 'pb', meta_ext='.meta.v2.csv')
df_tumor = pd.read_csv("../../paper_upn109/data/tcr/Tumor_scTCRB.csv")

# Convert kshape 0 to N
df_csf['kshape'] = df_csf['kshape'].astype(str).str.replace('0', 'N')
df_pb['kshape']  = df_pb['kshape'].astype(str).str.replace('0', 'N')

# label sample
df_csf['sample'] = 'CSF'
df_pb['sample'] = 'PB'
df_tumor['sample'] = df_tumor['Treatment']

def str_join(df, cols, sep=':'):
    return df.apply(lambda row: sep.join([str(row[x]) for x in cols]), axis=1)

df_csf['sample:kshape'] = df_csf['sample'] + ':' + df_csf['kshape'].astype(str)
df_pb['sample:kshape'] = df_pb['sample'] + ':' + df_pb['kshape'].astype(str)

# df_csf['sample:kshape'] = str_join(df_csf, ['sample', 'kshape'])
# df_pb['sample:kshape'] = str_join(df_pb, ['sample', 'kshape'])
df_tumor['sample:kshape'] = df_tumor['sample']

# Calculate AUC for bulk dataset and sample frequency for tumor scrnaseq 
df_csf['Freq'] = df_csf.loc[:, t_csf].sum(axis=1)
df_pb['Freq'] = df_csf.loc[:, t_pb].sum(axis=1)
df_tumor = normalize(df_tumor, 'sample', 'count', 'Freq')

# Concatenate all datasets
df_csf = df_csf.reset_index()
df_pb = df_pb.reset_index()
print(df_csf.head(), '\n',df_pb.head())
df = pd.concat([dfi[['TRB', 'Freq', 'sample', 'sample:kshape']] for dfi in [df_csf, df_pb, df_tumor]])

# Normalize frequency per sample
df = normalize(df, 'sample', 'Freq', 'FreqNorm')

csf_palette = {'1':'#6A51A3', '2':'#238B45','3':'#D94701', '4':'#CE1256'}
pbmc_palette = {'1':'#636363', '2':'#DE2D26','3':'#3182BD', '4':'#A6BDDB'}
tumor_palette = {'Pre': '#abd0e6', 'Post': '#3787c0'}
csf_palette = {'CSF:'+k:v for k,v in csf_palette.items()}
pbmc_palette = {'PB:'+k:v for k,v in pbmc_palette.items()}
shape_palette = {k:v for palette in [csf_palette, pbmc_palette, tumor_palette] \
    for k,v in palette.items() }

signal_noise_palette = {
    'PB:noise': '#FB9A99', 
    'PB:signal':'#E31A1C', 
    'CSF:noise': '#CAB2D6', 
    'CSF:signal': '#6A3D9A'}

shape_palette['CSF:N'] = signal_noise_palette['CSF:noise']
shape_palette['PB:N'] = signal_noise_palette['PB:noise']

# Overlap analysis
outdir = "../output/overlap/"
name = 'Shape'
overlap_shape = map_overlap(df, 'sample:kshape', 'TRB')
shape_order = ['Pre', 'Post'] + ['PB:N']+['PB:'+str(i+1) for i in range(4)] + \
    ['CSF:N']+['CSF:'+str(i+1) for i in range(4)] 
modes = [
            ('FreqNorm', np.sum, 'Frequency'), 
            ('TRB', pd.Series.nunique, 'Richness')]
plot_connection(overlap_shape, 'sample:kshape', shape_order, \
    shape_order, name, outdir, shape_palette, modes=modes)