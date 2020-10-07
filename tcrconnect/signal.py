import pandas as pd
def filter_mode(x):
    """
    Filter for values greater than the mode.
    Arguments:
        x: pandas.Series
    Return:
        Boolean pandas.Series, True for values that passed filter
    """
    mode = x.mode().values[0]
    return  x > mode

def filter_percentile(x, pct, method='first'):
    """
    Filter for values greater than the percentile.
    Arguments:
        x: pandas.Series
        pct: percentile cutoff (ex. 0.99 to keep top 1%)
    Return:
        Boolean pandas.Series, True for values that passed filter
    """
    rank = x.rank(ascending=True, pct=True, method=method)
    return rank > pct
    
def filter_knee(x, S):
    """
    Filter using knee detection. 
    Keeps values greater than the kneepoint
    Arguments:
        x: pandas.Series
    Return:
        Boolean pandas.Series, True for values that passed filter
    """
    from kneed import KneeLocator
    rank = x.rank(ascending=True, method='first', pct=True)
    kneedle = KneeLocator(rank, x, curve='convex', direction='increasing', S=S)
    return x > kneedle.knee

def get_nnz(s):
    return s.loc[s > 0]

def filter_columns(df, kind, columns, **kwargs):
    filters = {
        "mode": filter_mode,
        "percentile": filter_percentile,
        "knee": filter_knee
    }
    masks = []
    # loop through columns
    for t in columns:
        x = get_nnz(df[t])
        mask = filters[kind](x, **kwargs)
        masks.append(mask)
    df_mask = pd.concat(masks, axis=1, sort=False)  
    return df_mask

def rank_columns(df, columns):
    ranks = []
    for t in columns:
        x = get_nnz(df[t])
        rank = x.rank(ascending=True, method='first', pct=True)
        ranks.append(rank)
    df_rank = pd.concat(ranks, axis=1, sort=False)
    return df_rank

def merge_dfs(dfs, on):
    for df in dfs:
        df.set_index(on, inplace=True)
    merged = dfs[0].join(dfs[1:]).reset_index()
    for df in dfs:
        df.reset_index(inplace=True)
    return merged

def get_timepoints(df):
    """
    Extract timepoints and observational variables from dataframe column names
    """
    inds = df.columns.str.match(r"C\d+D\d+")
    return df.columns[inds], df.columns[~inds]

def tidy_timeseries(df):
    _, obs = get_timepoints(df)
    if df.index.name == 'TRB':
        df_tidy = pd.melt(df.reset_index(), 
        id_vars=['TRB'] + obs.tolist(), 
        var_name='Timepoint', value_name='Frequency')
    elif 'TRB' in df.columns.values:
        df_tidy = pd.melt(df, 
        id_vars=obs.tolist(), 
        var_name='Timepoint', value_name='Frequency')
    return df_tidy