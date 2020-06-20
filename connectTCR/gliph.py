import os
import re
import itertools
import pandas as pd
import numpy as np

def newCD(matchobj):
    return 'C'+matchobj.group(1).zfill(2)+'D'+matchobj.group(2)

def reformatCD(string):
    result = re.sub('C(\d+)D(\d+)', newCD, string)
    return result


def extractCD(string):
    result = re.search('C(\d+)D(\d+)', string)
    if result:
        return result[0]
    else:
        return string

def removeZero(string):
    return re.sub('0(\d)', r'\1', string)

def removeX(string):
    return re.sub('-X', '', string)

def renameTCRB(string):
    return re.sub('TCRB', 'TRB', string)

def cleanVJ(string):
    return renameTCRB(removeX(removeZero(string)))

def process_adaptive_bioidentity(path, sample, timepoints, exclude=[], 
    return_timepoints=True):
    """
    Process adaptive combined rearrangement file in bioidentity format.
    """
    df = pd.read_csv(path, sep='\t')
    
    columns = [col for col in df.columns if col not in exclude]
    df = df[columns]
    df.columns = [extractCD(reformatCD(col)) for col in df.columns]
    df['TcRb'] = df['Bioidentity'].apply(lambda x: x.split('+')[0])
    df['V'] = df['Bioidentity'].apply(lambda x: x.split('+')[1]).apply(cleanVJ)
    df['J'] = df['Bioidentity'].apply(lambda x: x.split('+')[2]).apply(cleanVJ)

    # create empty TRA column
    df['TcRa'] = np.nan

    # label sample name
    df['Sample'] = sample

    # Calculate sum of frequency from selected timepoints
    df['Freq'] = df.loc[:, timepoints].sum(axis=1)
    # keep non-zero entries
    df = df[df['Freq']!=0]
    vars  = ['TcRb', 'V', 'J', 'TcRa', 'Sample', 'Freq']
    if return_timepoints:
        return df[timepoints + vars]
    else:
        return df[vars]

def normalize_gliph_input(df, col='Freq', groupby='Sample'):
    df[col] = df.groupby([groupby])[col].transform(lambda x: x/sum(x))
    return df

def write_gliph_input(df_bio, outdir, name):
    columns = ['TcRb', 'V', 'J', 'TcRa', 'Sample', 'Freq'] 
    df_bio.loc[:, columns].to_csv(
        os.path.join(outdir,'gliph_input_{}.tsv'.format(name)), 
        sep='\t', header=False, index=False)
    return 

def read_gliph_input(gliphdir, name, path=None):
    columns = ['TcRb', 'V', 'J', 'TcRa', 'Sample', 'Freq'] 
    path = os.path.join(gliphdir, 'gliph_input_{}.tsv'.format(name))
    df_in = pd.read_csv(path, sep='\t', header=None)
    df_in.columns = columns
    df_in['TcRa'] = df_in['TcRa'].fillna('')
    return df_in

def read_gliph_output(path):
    df = pd.read_csv(path, sep=',')
    df['TcRa'] = df['TcRa'].fillna('')
    df['pattern-index'] = df['pattern'] + '-' + df['index'].astype(str)
    return df

def get_gliph_connections(df, groupby='pattern', 
    bioid=['TcRb', 'V', 'J', 'TcRa'], 
    sample_col='Sample', frequency_col='Freq'):
    grouped = df.groupby(groupby)
    resultlist = []
    for key,group in grouped:
        items = [tuple(x) for x in group[[*bioid, sample_col, frequency_col]].values]
        for b,g in itertools.permutations(items,2):
            resultlist.append([key,*b,g[0]])
    result = pd.DataFrame(resultlist, 
        columns=[groupby,*bioid, sample_col, frequency_col, 'to'])
    connection = result.groupby([sample_col, *bioid, 'to']).size().to_frame()
    connection.columns = ['connected']
    connection = connection.reset_index()
    connection['connected'] = connection['connected'] > 0
    df_connect = pd.pivot_table(connection, index=[sample_col, *bioid], 
        values='connected', columns=['to'], aggfunc=np.any)
    df_connect = df_connect.reset_index()
    return df_connect