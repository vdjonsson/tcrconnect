import numpy as np 
import os
import sys
sys.path.append('../../connectTCR')
from connectTCR.io import *

indir = '~/git/paper_upn109/data/tcr'
outdir = '../output/timeseries/'
if not os.path.isdir(outdir):
    os.system("mkdir "+outdir)

df = read_signal_noise(indir, 'CSF')

# remove TRBs with 0 at all timepoints
n_i = df.shape[0]
df = df.loc[df.sum(axis=1) > 0]
n_f = df.shape[0]
print(n_i, n_f)
savename = 'csf'
write_columns_index(df, outdir, savename)
write_npz(df, outdir, savename)
files = [outdir+savename+ext for ext in ['.npz', '.columns', '.index']]
df_reload = read_npz(*files)

assert np.all(df_reload.values == df.values)
assert np.all(df_reload.columns.values == df.columns.values)
assert np.all(df_reload.index.values == df.index.values)

df = read_signal_noise(indir, 'PBMC')

# remove TRBs with 0 at all timepoints
n_i = df.shape[0]
df = df.loc[df.sum(axis=1) > 0]
n_f = df.shape[0]
print(n_i, n_f)

savename = 'pb'
write_columns_index(df, outdir, savename)
write_npz(df, outdir, savename)
files = [outdir+savename+ext for ext in ['.npz', '.columns', '.index']]
df_reload = read_npz(*files)

assert np.all(df_reload.values == df.values)
assert np.all(df_reload.columns.values == df.columns.values)
assert np.all(df_reload.index.values == df.index.values)
