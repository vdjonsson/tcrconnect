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
        for col in [True, False]:
            if col not in m.columns:
                m[col] = 0
        m = m.rename(columns={False:'Not'+dest, True:dest})
        m = m.fillna(0)
        m.columns.name = None
        m.index.name = None
        dfs.append(m)
        if show_df:
            print(m)
    
    mat = pd.concat(dfs, axis=1)
    print("Missing groups:", [x for x in groupby_order if x not in mat.index.values])
    print("Missing destinations:", [x for x in destinations if x not in mat.columns.values])
    # entry i,j  is flux from i to j
    mat = mat.loc[groupby_order, destinations].fillna(0)
    if show_mat:
        print(mat)
    return mat, dfs