import pandas as pd
import numpy as np
import os, sys, glob
from multiprocessing import Pool

GAIADIR = os.getenv('GAIADATA', os.path.expanduser('~/.gaia'))
DATADIR = os.getenv('TGASTARS', os.path.expanduser('~/.tgastars'))
STARMODELDIR = os.path.join(DATADIR, 'starmodels')

try:
    TGAS = pd.read_hdf(os.path.join(GAIADIR, 'TgasSource.h5'), 'df')
except IOError:
    print('Run tgastars-write-tgas-hdf first. Exiting.')
    sys.exit()

def source_id(i):
    if i > len(TGAS):
        return i
    else:
        return TGAS.iloc[i].source_id

def dirname(i):
    """Returns directory name, given index
    """
    gid = source_id(i)

    return os.path.join(DATADIR, 'starmodels', str(gid)[:3], str(gid))


def _get_ini_files(d):
    ini_files = glob.glob('{}/*/star.ini'.format(d))
    return [os.path.basename(os.path.dirname(f))
                for f in ini_files]

def update_completed(processes=1, test=False):
    all_stars = []
    dirs = [os.path.join(STARMODELDIR, d) for d in os.listdir(STARMODELDIR)]
    if test: 
        dirs = dirs[:20]

    pool = Pool(processes=processes)
    all_stars = pool.map(_get_ini_files, dirs)

    all_stars = np.array([x for y in all_stars for y in x])
    np.random.sort(all_stars)
    if test:
        print(all_stars)
    else:
        np.savetxt(os.path.join(DATADIR, 'completed.list'), all_stars, fmt='%s')


def get_completed():
    """
    returns list of stellar IDs that have been fit
    """
