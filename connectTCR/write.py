import os

from scipy.sparse import csr_matrix, save_npz
from scipy.io import mmwrite

def write_columns_index(df, outdir, save_name):
    with open(os.path.join(outdir, save_name+'.columns'), 'w') as f:
        for item in df.columns.values:
            f.write("%s\n" % item)
    with open(os.path.join(outdir, save_name+'.index'), 'w') as f:
        for item in df.index.values:
            f.write("%s\n" % item)

def write_npz(df, outdir, save_name):
    """
    Write pandas dataframe as sparse matrix (csr format)
    Arguments:
        df: pandas.DataFrame to be converted and saved as sparse matrix
        outdir: Output directory
        save_name: Prefix used to name generated files
    Return:
        Generates in outdir with prefix save_name:
            1) npz file 'save_name.npz'

    """
    mat = csr_matrix(df.values)
    save_npz(os.path.join(outdir, save_name+'.npz'), mat)

def write_mtx(df, outdir, save_name, precision=30):
    """
    Write pandas dataframe as sparse matrix (COO format)
    Arguments:
        df: pandas.DataFrame to be converted and saved as sparse matrix
        outdir: Output directory
        save_name: Prefix used to name generated files
    Return:
        Generates in outdir with prefix save_name:
            1) mtx file 'save_name.mtx'
    """
    mat = csr_matrix(df.values)
    mmwrite(os.path.join(outdir, save_name+'.mtx'), mat, precision=precision)