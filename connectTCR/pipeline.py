
import numpy as np
import pandas as pd

from connectTCR.connection import flux
from connectTCR.plotting import barplot

def plot_connection(overlap, groupby, groupby_order, destinations, name, outdir, \
    palette, modes=None):
    if modes is None:
        modes = [
            ('FreqNorm', np.sum, 'Frequency'), 
            ('TcRb', pd.Series.nunique, 'Richness')]
    for mode in modes:
        value_key, func, estimator = mode
        mode_name = '{}_{}'.format(estimator, name)
        mat, _ = flux(overlap, groupby, groupby_order=groupby_order, 
        destinations=destinations, value_key=value_key, func=func)
        mat.to_csv(outdir+'flux_{}.csv'.format(mode_name))
        mat_norm = mat.apply(lambda x: x / x.sum(), axis=1)
        mat.to_csv(outdir+'relative_flux_{}.csv'.format(mode_name))
        barplot(mat, palette, normalize=True, ylabel='Relative '+estimator, 
            outdir=outdir, save='Relative_'+mode_name)
        barplot(mat, palette, normalize=False, ylog=True, 
            stacked=False, ylabel=estimator, figsize=(6,2), width=0.8, 
            outdir=outdir, save=mode_name)
    return 