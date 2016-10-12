import pandas as pd
import numpy as np
import os, sys, glob, re
import logging
from multiprocessing import Pool
#from multiprocessing.pool import ThreadPool as Pool

GAIADIR = os.getenv('GAIADATA', os.path.expanduser('~/.gaia'))
DATADIR = os.getenv('TGASTARS', os.path.expanduser('~/.tgastars'))
STARMODELDIR = os.path.join(DATADIR, 'starmodels')
TGASPATH = os.path.join(GAIADIR, 'TgasSource.h5')

try:
    TGAS = pd.read_hdf(TGASPATH, 'df')
except IOError:
    logging.warning('Run tgastars-write-tgas-hdf first!')
    TGAS = None

def source_id(i):
    i = int(i)
    if i > len(TGAS):
        return i
    else:
        return TGAS.iloc[i].source_id

def get_row(i):
    """Returns either row index i or by source_id
    """
    if i < len(TGAS):
        ind = i
    else:
        ind = np.where(TGAS.source_id==i)[0][0]
    return TGAS.iloc[ind]

def get_Gmag(i):
    s = get_row(i)
    return s.phot_g_mean_mag, 0.02

def binary_index(i):
    """Returns i1, i2  (i1 < i2) 

    If doesn't match expected patterns, raises ValueError
    """
    if type(i)==type(''):
        m = re.search('(\d+)-(\d+)', i)
        if m:
            i1, i2 = int(m.group(1)), int(m.group(2))
        else:
            raise ValueError('{} not a binary pattern'.format(i))
    elif hasattr(i, '__iter__'):
        if len(i)==2:
            i1, i2 = i
        else:
            raise ValueError
    else:
        raise ValueError

    imin = min(i1, i2)
    imax = max(i1, i2)

    return imin, imax

def dirname(i, rootdir=STARMODELDIR):
    """Returns directory name, given index (or two indicies)

    Can also pass string like '125120-12041' or a tuple of indices (12512, 125012).
    First attempted to be parsed by `binary_index`
    """
    try:
        # Binary index.
        i1, i2 = binary_index(i)
        return os.path.join(rootdir, 'binaries', '{}-{}'.format(i1, i2))
    except ValueError:
        # just a single index
        gid = source_id(i)
        return os.path.join(rootdir, str(gid)[:3], str(gid))


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
        np.savetxt(os.path.join(DATADIR, 'all_test.list'), all_stars, fmt='%s')
    else:
        np.savetxt(os.path.join(DATADIR, 'all.list'), all_stars, fmt='%s')

    print('{} written.'.format(os.path.join(DATADIR, 'all.list')))

    ready_stars = np.array(list(set(all_stars) - set(done_stars)))
    ready_stars.sort()
    if test:
        np.savetxt(os.path.join(DATADIR, 'ready_test.list'), ready_stars, fmt='%s')
    else:
        np.savetxt(os.path.join(DATADIR, 'ready.list'), ready_stars, fmt='%s')

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
