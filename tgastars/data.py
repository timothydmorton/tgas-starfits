import pandas as pd
import numpy as np
import os, sys, glob
from multiprocessing import Pool
#from multiprocessing.pool import ThreadPool as Pool

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

def _get_h5_files(d, modelname='dartmouth_starmodel_single'):
    h5_files = glob.glob('{}/*/{}.h5'.format(d,modelname))
    return [os.path.basename(os.path.dirname(f))
                for f in h5_files]

def update_completed(processes=1, test=False):


    dirs = [os.path.join(STARMODELDIR, d) for d in os.listdir(STARMODELDIR)]
    if test: 
        dirs = dirs[:20]

    pool = Pool(processes=processes)

    done_stars = np.array([x for y in pool.map(_get_h5_files, dirs) for x in y])
    done_stars.sort()
    if test:
        np.savetxt(os.path.join(DATADIR, 'completed_test.list'), done_stars, fmt='%s')
    else:
        np.savetxt(os.path.join(DATADIR, 'completed.list'), done_stars, fmt='%s')

    print('{} written.'.format(os.path.join(DATADIR, 'completed.list')))

    all_stars = np.array([x for y in pool.map(_get_ini_files, dirs) for x in y])
    all_stars.sort()
    if test:
        np.savetxt(os.path.join(DATADIR, 'ready_test.list'), all_stars, fmt='%s')
    else:
        np.savetxt(os.path.join(DATADIR, 'ready.list'), all_stars, fmt='%s')

    print('{} written.'.format(os.path.join(DATADIR, 'ready.list')))


def get_completed_ids():
    """
    returns list of stellar IDs that have been fit
    """
    return np.loadtxt(os.path.join(DATADIR, 'completed.list'), dtype=int)

def get_ready_ids():
    """
    returns list of stellar IDs that have been fit
    """
    return np.loadtxt(os.path.join(DATADIR, 'ready.list'), dtype=int)
