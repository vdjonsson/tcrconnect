import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from connectTCR.connection import flux
from connectTCR.plotting import barplot
from connectTCR.mapping import map_gliph
from connectTCR.utils import clean_variable

def plot_connection(overlap, groupby, groupby_order, destinations, name, outdir, \
    palette, modes=None, stacked_figsize=(2,2), unstacked_figsize=(4,2)):
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
        mat_norm.to_csv(outdir+'relative_flux_{}.csv'.format(mode_name))
        barplot(mat, palette, normalize=True, ylabel='Relative '+estimator, 
            outdir=outdir, save='Relative_'+mode_name, figsize=stacked_figsize)
        barplot(mat, palette, normalize=False, ylog=True, 
            stacked=False, ylabel=estimator, width=0.8, 
            outdir=outdir, save=mode_name, figsize=unstacked_figsize)
    return 

def plot_multi_connections(overlap, groupby, groupby_order, destinations_list, name, outdir, \
    palette, modes=None, figsize=(2,2), align='edge',widths=[-0.4, 0.4], **kwargs):
    if modes is None:
        modes = [
            ('FreqNorm', np.sum, 'Frequency'), 
            ('TcRb', pd.Series.nunique, 'Richness')]
    for mode in modes:
        value_key, func, estimator = mode
        mode_name = '{}_{}'.format(estimator, name)
        fig, ax = plt.subplots(figsize=figsize)
        
        for destinations, width in zip(destinations_list, widths):
            mat, _ = flux(overlap, groupby, groupby_order=groupby_order, 
            destinations=destinations, value_key=value_key, func=func)
            mat.to_csv(outdir+'flux_{}.csv'.format(mode_name))
            mat_norm = mat.apply(lambda x: x / x.sum(), axis=1)
            mat_norm.to_csv(outdir+'relative_flux_{}.csv'.format(mode_name))
            barplot(mat, palette, ax=ax, normalize=True, ylabel='Relative '+estimator, 
                outdir=outdir, save='Relative_'+mode_name, 
                align='edge', width=width, xlim = (-1, len(mat)), **kwargs)
    return 

def gliph_connection(df_in, df_out, key, outdir, name=None):
    df_in_connect, df_out_connect = map_gliph(df_in, df_out, 'index', key)
    comps = df_in_connect[key].unique()
    df_in_connect['Connected'] = df_in_connect[comps].any(axis=1)
    if name is None:
        name = clean_variable(key)
    df_in_connect.to_csv(
        os.path.join(outdir, "gliph_connection_{}.csv".format(name)), 
        index=False)
    df_out_connect.to_csv(
        os.path.join(outdir, "gliph_clusters_{}.csv".format(name)), 
        index=False)
    return df_in_connect

def gliph_connected_mat(df_in_connect, key, groupby, outdir, name=None):
    connection = df_in_connect.groupby([groupby, 'Connected'])['Freq'].sum().unstack()
    connection = connection.rename(columns={True:'Connected', False: 'Not Connected'})
    order = ['Connected', 'Not Connected']
    connection = connection[order]
    if name is None:
        name = clean_variable(key)
    connection.to_csv(
        os.path.join(outdir, "gliph_connected_{}_per_{}.csv".format(
            name, clean_variable(groupby))), 
        )
    return connection
