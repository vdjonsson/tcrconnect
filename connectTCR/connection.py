from typing import Optional, Union, Iterable, Dict

import pandas as pd
import numpy as np

def flux(
    df: pd.core.frame.DataFrame, 
    groupby:str, 
    groupby_order: Optional[list]=None,
    destinations: Optional[list]=None, 
    value_key:str='FreqNorm', 
    func=np.sum, 
    show_df: Optional[bool]=False, 
    show_mat: Optional[bool]=False):
    """
    Args:
        df: Input dataframe 
        groupby: Column used to determine the groups to groupby
        destinations: List of boolean columns for which to calculate flux.
            True values indicate connection
        value_key: Column in df used for calculating flux (ex. TcRb, FreqNorm)
        groupby_order: Order of groups in the final matrix
        func: function to apply to the values with connection per group 
            (ex. np.sum, pd.Series.nunique)
        show_df: Print flux of each group if True
        show_mat: Print flux matrix if True

    Example:
        Sum Normalized Frequency: value_key='FreqNorm', func=np.sum
        Richness(# unique TRB): value_key='TcRb', func=pd.Series.nunique
    """
    dfs = []

    if groupby_order is None:
        groupby_order = df[groupby].unique()

    if destinations is None:
        destinations = df[groupby].unique()
    
    for dest in destinations:
        # calculate estimator of value_key from each groupby category (row) to destination (col)
        m = df.groupby([groupby,dest])[value_key].apply(func).to_frame().unstack().fillna(0)
        m.columns = m.columns.get_level_values(1)
        m = m.loc[groupby_order] # reorder
        m = m.rename(columns={False:'Not'+dest, True:dest})
        m = m.fillna(0)
        del m.columns.name
        del m.index.name
        dfs.append(m)
        if show_df:
            print(m)
        
    # entry i,j  is flux from i to j
    mat = pd.concat(dfs, axis=1).loc[groupby_order, destinations].fillna(0)
    if show_mat:
        print(mat)
    return mat, dfs