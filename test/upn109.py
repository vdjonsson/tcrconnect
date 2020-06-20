import os
import pandas as pd
import seaborn as sns

import sys
sys.path.append('../../connectTCR/')

from connectTCR.utils import import_gliph_input, normalize
from connectTCR.mapping import map_signal_noise, map_shape_cluster, map_overlap
from connectTCR.connection import flux
from connectTCR.plotting import set_figure_params, barplot
from connectTCR.pipeline import plot_connection

gliphdir = '../data/gliph'
dataset = 'blood-csf-tumor'

outdir = '../output/{}/'.format(dataset)
if not os.path.isdir(outdir):
    os.system('mkdir -p '+outdir)

# import gliph input file
df_in = import_gliph_input(gliphdir, dataset, suffix='_general')

# Rename samples
names = {'blood':'PB', 'csf':'CSF', 'PBT103-1':'Pre', 'PBT120':'Post'}
df_in['Sample'] = df_in['Sample'].map(names)

# Normalize frequency per sample
df_in = normalize(df_in, 'Sample', 'Freq', 'FreqNorm')

# map signal vs noise
name = {'CSF':'CSF', 'PB':'PBMC'}
signaldir = '../data/tcr_dynamics/'
sample2signal = {comp:pd.read_csv(signaldir+'{c}(Signal).csv'.format(c=name[comp]), index_col=0).reset_index() \
    for comp in name }
df_in = map_signal_noise(df_in, sample2signal, 'Sample', 'TcRb', 'index')

# map shape cluster
from scvi_analysis.tcr import get_dynamic_classes
tcrdir = '../data/tcr_dynamics/'
csfshape = get_dynamic_classes(tcrdir, 'SignalCSFKmeans', 'CSFShapeKmeansMap')
bloodshape = get_dynamic_classes(tcrdir, 'SignalPBMCKmeans', 'PBMCShapeKmeansMap')
sample2shapemap = {'CSF:Signal':csfshape, 'PB:Signal':bloodshape}
df_in = map_shape_cluster(df_in, sample2shapemap, 'Sample:Signal/Noise', 'TcRb')
df_in['Sample:ShapeCluster'] = df_in['Sample:Signal/Noise:ShapeCluster'].str.replace( \
    ':Signal', '', regex=True)
# set high-res and paper context
set_figure_params()

# color palettes 
csf_palette = {'Shape4':'#238b45', 'Shape2':'#d94701', 'Shape1':'#6a51a3', 'Shape3':'#ce1256'}
pbmc_palette = {'Shape1':'#de2d26', 'Shape2':'#3182bd', 'Shape3':'#636363', 'Shape4':'#2ca25f', 'Shape5':'#a6bddb'}
tumor_palette = {'Pre': '#abd0e6', 'Post': '#3787c0'}
csf_palette = {'CSF:'+k:v for k,v in csf_palette.items()}
pbmc_palette = {'PB:'+k:v for k,v in pbmc_palette.items()}
shape_palette = {k:v for palette in [csf_palette, pbmc_palette, tumor_palette] \
    for k,v in palette.items() }

paired = sns.color_palette('Paired',10)[4:6] + sns.color_palette('Paired',10)[-2:]
signal_noise_palette = {x:c for x, c in zip(['PB:Noise', 'PB:Signal', 'CSF:Noise', 'CSF:Signal'], paired)}
for x in tumor_palette:
    signal_noise_palette[x] = tumor_palette[x]

signal_noise_order = ['PB:Signal', 'PB:Noise', 'CSF:Signal', 'CSF:Noise', 'Pre', 'Post']
shape_order = ['Pre', 'Post'] + ['PB:Shape'+str(i+1) for i in range(5)] + ['PB:Noise'] + \
    ['CSF:Shape'+str(i+1) for i in range(4)] + ['CSF:Noise']

all_palette = shape_palette.update(signal_noise_palette)
print(df_in.columns)
df_in.to_csv('{}/gliph_input_{}_general_mapped.csv'.format(outdir, dataset), index=False)
# overlap for signal/noise
'''
name = 'Signal_Noise'
overlap_signal_noise = map_overlap(df_in, 'Sample:Signal/Noise', 'TcRb')
plot_connection(overlap_signal_noise, 'Sample:Signal/Noise', signal_noise_order, \
    signal_noise_order, name, outdir, signal_noise_palette)

name = 'Signal_Noise_Per_Shape'
plot_connection(overlap_signal_noise, 'Sample:ShapeCluster', shape_order, \
    signal_noise_order, name, outdir, signal_noise_palette)

# overlap for shapes
name = 'Shape'
overlap_shape = map_overlap(df_in, 'Sample:ShapeCluster', 'TcRb')

plot_connection(overlap_shape, 'Sample:ShapeCluster', shape_order, \
    shape_order, name, outdir, shape_palette)
'''