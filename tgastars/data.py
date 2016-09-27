import pandas as pd
import os

GAIADIR = os.getenv('GAIADATA', os.path.expanduser('~/.gaia'))
DATADIR = os.getenv('TGASTARS', os.path.expanduser('~/.tgastars'))

try:
    TGAS = pd.read_hdf(os.path.join(GAIADIR, 'TgasSource.h5'), 'df')
except IOError:
    print('Run tgastars-write-tgas-hdf first. Exiting.')
    sys.exit()

def source_id(i):
    return TGAS.iloc[i].source_id

def dirname(i):
    """Returns directory name, given index
    """
    gid = source_id(i)
    return os.path.join(DATADIR, 'starmodels', str(gid))
