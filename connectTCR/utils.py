import os
import glob
import pandas as pd

bio_id = ['TcRb', 'V', 'J', 'TcRa', 'Sample']

def check_dir(path):
    if not os.path.isdir(path):
        raise ValueError('Path is not a directory.')
    if path[-1] != '/':
        return path + '/'
    else:
        return path

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
    path = check_dir(gliphdir) + dataset + '/gliph_input_' + dataset + suffix + '.tsv'
    df_in = pd.read_csv(path, sep='\t', header=None)
    df_in.columns = bio_id + ['Freq']
    df_in['TcRa'] = df_in['TcRa'].fillna('')
    return df_in

def import_gliph_output(gliphdir, dataset, suffix=''):
    path = check_dir(gliphdir) + dataset + '/gliph_output_' + dataset + suffix + '.csv'
    df_out = pd.read_csv(path, sep=',')
    df_out['TcRa'] = df_out['TcRa'].fillna('')
    return df_out

def read_kmeans(tcrdir, prefix):
    files = glob.glob('{}{}*.csv'.format(tcrdir, prefix))
    dfs = []
    names = []
    for f in files:
        dfs.append(pd.read_csv(f).rename(columns={'Unnamed: 0':'TCR'}))
        names.append(f.split(tcrdir)[1].split('.csv')[0])
    kmeans = [int(name.split(prefix)[1]) for name in names]
    return dfs, names, kmeans

def get_dynamic_classes(tcrdir, prefix, shapemap):
    dfs, names, kmeans = read_kmeans(tcrdir, prefix)
    trb2kmeans = {tcr:i for df, i in zip(dfs, kmeans) for tcr in df['TCR']}
    df_class = pd.read_csv('{}{}.csv'.format(tcrdir, shapemap))
    kmeans2shape = {int(i):('Shape'+str(j)) for i, j in zip(df_class['Kmeans'], df_class['Shape'])}
    trb2shape = {tcr:kmeans2shape[trb2kmeans[tcr]] for tcr in trb2kmeans}
    return trb2shape

def get_trb_groups(df, trb, trb_col='TcRb', groupby='index', 
    cols=None, save=False, savedir='./'):
    if cols is None:
        cols = df.columns
    # filter by trb
    inds_trb = df[trb_col]==trb
    # get associated groups 
    groups = df.loc[inds_trb, groupby].unique()
    # filter by groups
    inds_group = df[groupby].isin(groups)
    
    df_trb_groups = df.loc[inds_group, cols]
    if save:
        filename = '{}_{}.csv'.format(trb, groupby)
        df_trb_groups.to_csv(check_dir(savedir)+filename, index=False)
    return df_trb_groups

