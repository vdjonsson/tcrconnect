from typing import Optional, Union, Iterable, Dict
import os
import collections

import pandas as pd
import numpy as np

def map_signal_noise(
    df: pd.core.frame.DataFrame, 
    sample2signal: Dict[str, pd.core.frame.DataFrame], 
    sample_key: str, 
    df_key: str, 
    signal_key: str, 
    new_key: Optional[str] = 'Signal/Noise'):
    """
    Args:
        df: input dataframe 
        sample2signal: mapping of str to dataframe of signals
        sample_key: Column containing sample labels
        df_key: Column in df containing TCR sequence
        signal_key: Column in signal dataframes containign TCR sequence  
        new_key: Column to store signal/noise labels
    Returns:
        df: copy of dataframe with added Signal/Noise and Sample:Signal/Noise columns
    """
    df = df.copy() 
    # Construct dictionary for mapping signals per sample
    signals = collections.defaultdict(bool)
    for sample, df_signal in sample2signal.items():
        for trb in df_signal[signal_key].values:
            signals[(sample, trb)] = True

    
    df[new_key] = df.set_index([sample_key, df_key]).index.map(signals)
    # convert to string labels
    df[new_key] = df[new_key].map({True:'Signal', False:'Noise'}) 
    # find samples without signal/noise determination
    undetermined = ~df[sample_key].isin(sample2signal)
    # remove labels for undetermined samples
    df[new_key] = df[new_key] * ~undetermined
    # 
    df[sample_key + ':' + new_key] = df[sample_key] + \
        (undetermined.map({False:':', True:''})) + df[new_key] 
    return df

def map_shape_cluster(
    df: pd.core.frame.DataFrame,
    sample2shapemap: Dict[str, Dict[str, str]],
    sample_key: str, 
    tcr_key: str, 
    new_key: Optional[str] = 'ShapeCluster'
    ):
    """
    Args:
        df: input dataframe 
        sample2shapemap: mapping of str to mapping of signals TCR to shape clusters
        sample_key: Column containing sample labels
        tcr_key: Column in df containing TCR sequence
        new_key: Column to store shape cluster labels
    Returns:
        df: copy of dataframe with added Signal/Noise and Sample:Signal/Noise columns
    """
    df = df.copy()
    allshapecluster = collections.defaultdict(str)
    
    for sample, trb2shape in sample2shapemap.items():
        shapecluster = collections.defaultdict(str, {(sample, k):v for k,v in trb2shape.items()})
        # map each compartment separately
        df[sample+new_key] = df.set_index([sample_key, tcr_key]).index.map(shapecluster)
        for trb in trb2shape:
            # make combined dictionary mapping to shape with compartment prefix
            allshapecluster[(sample, trb)] = sample+':'+trb2shape[trb]

    df[new_key] = df.set_index([sample_key, tcr_key]).index.map(allshapecluster)
    # find samples without shape cluster determination
    undetermined = ~df[sample_key].isin(sample2shapemap)
    df[sample_key+':'+new_key] = df[sample_key]*undetermined + df[new_key]

    return df

def map_overlap(
        df:pd.core.frame.DataFrame, 
        groupby: str, 
        key: str):
    """
    Args:
        df: Input dataframe 
        groupby: Column used to determine the groups to groupby
        key: Column used to compare overlap
    Returns:
        df: copy of dataframe with added boolean columns for each group.
        df[i, group] is presence of df[i, key] in df[df[groupby]==group, key] 
    
    For performance, we avoid using pandas.Series.transform and pandas.Series.isin
    """
    df = df.copy() # avoid modifying input dataframe
    # get groups
    gb = df.groupby(groupby)
    
    #  find incidence of value in key per group
    for group, df_i in gb:
        # dictionary mapping values to True
        value_in_group = collections.defaultdict(bool, (df_i[key].value_counts()>0).to_dict())
        # values not in dictionary gets False by default
        df[group] = df[key].map(value_in_group)
        # remove self overlap
        df.loc[df[groupby]==group, group] = False
    return df

def map_gliph(df_in, df_out, groupby, key):
    df_in = df_in.copy()
    df_out = df_out.copy()
    bio_id = ['TcRb', 'V', 'J', 'TcRa', 'Sample']
    # groupby specificity groups
    gb =  df_out.groupby(groupby)
    # categories in key
    comps = df_in[key].unique()
    sample_in_gliph = collections.defaultdict(bool, (gb[key].value_counts()>0).to_dict())
    sample_count_per_gliph = gb[key].value_counts().to_dict()
    sample_count = df_out.set_index([groupby, key]).index.map(sample_count_per_gliph)
    for comp in comps:
        # find incidence of sample per gliph group
        df_out['has'+comp] = comp # string place holder for mapping
        df_out['has'+comp] = df_out.set_index([groupby, 'has'+comp]).index.map(sample_in_gliph)
        # find singleton self
        df_out[comp+'_singleton_self'] = (df_out[key]==comp) & (sample_count == 1)
        # count self connection involving >=2 tcrs
        df_out[comp] = df_out['has'+comp]&~df_out[comp+'_singleton_self'] 
        # map connection to input dataframe by trb, v, j, tra, sample
        df_in[comp] = df_in.set_index(bio_id).index.map(df_out.groupby(bio_id)[comp].any().to_dict())
        df_in[comp] = df_in[comp].fillna(False)
        
    return df_in, df_out