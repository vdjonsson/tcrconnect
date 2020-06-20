import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import sys
sys.path.append('../../connectTCR')
from connectTCR.io import *
from connectTCR.signal import *
from connectTCR.utils import *
from connectTCR.gliph import *
from connectTCR.mapping import map_overlap
from connectTCR.pipeline import plot_connection

import figure_settings

df_in = read_gliph_input("../data/gliph/blood-csf-tumor", "blood-csf-tumor_general")
df_out = read_gliph_output("../data/gliph/blood-csf-tumor/gliph_output_blood-csf-tumor_general.csv")
df_out_no_single = df_out.loc[(df_out['pattern']!='single')]
map_gliph(df_in, df_out_no_single, 'index', 'Sample')

tsdir = '../output/timeseries/'
meta_pb = pd.read_csv(tsdir+'pb.meta.v2.csv')
meta_pb['sample'] = 'blood' 
meta_csf = pd.read_csv(tsdir+'csf.meta.v3.csv')
meta_csf['sample'] = 'csf' 
meta = pd.concat([meta_csf, meta_pb])
meta['sample:kshape'] = meta['sample'] + ':' + meta['kshape'].astype(str)

merged = df_in.merge(meta, left_on=['TcRb', 'Sample'], right_on=['TRB', 'sample'], how='inner')
merged['Connected'] = merged[['blood', 'csf', 'PBT103-1', 'PBT120']].any(axis=1)