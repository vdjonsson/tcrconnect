import os

import pandas as pd
import scipy.sparse

def read_npz(npz, columns, index):
    """
    Read npz sparse data files into dense pandas dataframe.
    Arguments:
        npz(str): path to npz file of sparse matrix
        columns(str): path to txt file with column headers
        index(str): path to txt file with index names
    Return:
        df: pandas.DataFrame
    """
    mat = scipy.sparse.load_npz(npz)
    columns = pd.read_csv(columns, header=None)[0].values
    index =  pd.read_csv(index, header=None)[0].values
    return pd.DataFrame(mat.toarray(), index=index, columns=columns)

def read_mtx(mtx, columns, index):
    mat = scipy.io.mmread(mtx)
    columns = pd.read_csv(columns, header=None)[0].values
    index =  pd.read_csv(index, header=None)[0].values
    return pd.DataFrame(mat.toarray(), index=index, columns=columns)

def read_signal_noise(indir, comp):
    """
    Load old signal and noise files inside input directory.
    Nan TRBs are removed. 
    Arguments:
        indir (str): Input directory
        comp (str): Compartment name of signal and noise files.
    Return:
        df: pandas.DataFrame of concatenated signal and noise timeseries.
    """
    noise = pd.read_csv(os.path.join(indir, comp+'(Noise).csv'))
    signal = pd.read_csv(os.path.join(indir, comp+'(Signal).csv'))
    df = pd.concat([noise, signal]).set_index('TRB')
    # drop nan
    df = df.loc[df.index.dropna()]
    return df

def read_timeseries(indir, name, meta_ext='.meta.csv'):
    """
    Load sparse data files and metadata into dense pandas dataframe.
    Arguments:
        indir (str): Path to input directory
        name (str): Prefix of input files
    Returns:
        tuple:
            df: pandas.DataFrame with additional columns of metadata
            columns: column names prior to adding metadata
    """
    files = [indir+name+ext for ext in ['.npz', '.columns', '.index']]
    df = read_npz(*files)
    columns = df.columns
    meta = pd.read_csv(indir+name+meta_ext, index_col='TRB')
    df = pd.concat([df, meta], axis=1, sort=False)
    df.index.name = 'TRB'
    return df, columns

