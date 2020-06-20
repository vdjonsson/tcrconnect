import os
import pandas as pd

import sys
sys.path.append('../../connectTCR')

from connectTCR.utils import import_gliph_output, normalize, get_dynamic_classes, get_trb_groups
from connectTCR.mapping import map_signal_noise, map_shape_cluster, map_overlap
from connectTCR.connection import flux
from connectTCR.plotting import set_figure_params, barplot
from connectTCR.pipeline import plot_connection

gliphdir = '../data/gliph'
dataset = 'blood-signal-csf-signal-tumor'

outdir = '../output/{}/'.format(dataset)
if not os.path.isdir(outdir):
    os.system('mkdir -p '+outdir)

df = import_gliph_output(gliphdir, dataset, suffix='_general')
# Rename samples
names = {'blood':'PB', 'csf':'CSF', 'PBT103-1':'Pre', 'PBT120':'Post'}
df['Sample'] = df['Sample'].map(names)

# map signal vs noise
name = {'CSF':'CSF', 'PB':'PBMC'}
signaldir = '../data/tcr/'
sample2signal = {comp:pd.read_csv(signaldir+'{c}(Signal).csv'.format(c=name[comp]), index_col=0).reset_index() \
    for comp in name }
df = map_signal_noise(df, sample2signal, 'Sample', 'TcRb', 'index')

# map shape cluster
tcrdir = '../data/tcr/'
csfshape = get_dynamic_classes(tcrdir, 'SignalCSFKmeans', 'CSFShapeKmeansMap')
bloodshape = get_dynamic_classes(tcrdir, 'SignalPBMCKmeans', 'PBMCShapeKmeansMap')
sample2shapemap = {'CSF:Signal':csfshape, 'PB:Signal':bloodshape}
df = map_shape_cluster(df, sample2shapemap, 'Sample:Signal/Noise', 'TcRb')
df['Sample:ShapeCluster'] = df['Sample:Signal/Noise:ShapeCluster'].str.replace( \
    ':Signal', '', regex=True)

cols= ['index', 'pattern', 'Fisher_score', 'number_subject', 
    'number_unique_cdr3', 'final_score', 'hla_score', 
    'vb_score', 'expansion_score', 'length_score', 
    'cluster_size_score', 'type', 
    'ulTcRb', 'TcRb', 'V', 'J', 'TcRa', 'Sample', 'Freq', 
    'Sample:Signal/Noise', 'Sample:ShapeCluster']
df.loc[:,cols].to_csv('{}/gliph_output_{}_general_mapped.csv'.format(outdir, dataset), index=False)