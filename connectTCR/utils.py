import pandas as pd

bio_id = ['TcRb', 'V', 'J', 'TcRa', 'Sample']

def normalize(df, groupby, key, new_key):
    """
    Normalize values by sum per group 
    Args:
        df: input dataframe 
        groupby: Column used to determine the groups to groupby
        key: Column to normalize
        new_key: Column to store normalized values
    Returns:
        df: copy of dataframe with normalized values stored in new_key.
    
    For performance, we avoid using pandas.Series.transform
    """
    df = df.copy()
    # avoid pd.Series.transform to improve performance
    group_sum = df.groupby(groupby)[key].sum().to_dict()
    df[new_key] = df[key] / df.set_index(groupby).index.map(group_sum)

    return df

def import_gliph_input(gliphdir, dataset, suffix=''):
    bio_id = ['TcRb', 'V', 'J', 'TcRa', 'Sample']
    path = gliphdir + dataset + '/gliph_input_' + dataset + suffix + '.tsv'
    df_in = pd.read_csv(path, sep='\t', header=None)
    df_in.columns = bio_id + ['Freq']
    df_in['TcRa'] = df_in['TcRa'].fillna('')
    return df_in

def import_gliph_output(gliphdir, dataset, suffix=''):
    path = gliphdir + dataset + '/gliph_output_' + dataset + suffix + '.csv'
    df_out = pd.read_csv(path, sep=',')
    df_out['TcRa'] = df_out['TcRa'].fillna('')
    return df_out

def import_timeseries(tcrdir, dataset):
    return 
    
