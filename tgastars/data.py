import pandas as pd
import numpy as np
import os, sys, glob

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

def update_completed():
    all_stars = []
    dirs = os.listdir(STARMODELDIR)

    for d in dirs:
        d = os.path.join(STARMODELDIR, d)
        if not os.path.isdir(d):
            continue
        ini_files = glob.glob('{}/*/star.ini'.format(d))
        all_stars = all_stars + [os.path.basename(os.path.dirname(f))
                                 for f in ini_files]

    all_stars = np.array(all_stars)
    np.random.sort(all_stars)
    np.savetxt(os.path.join(DATADIR, 'completed.list'), all_stars, fmt='%s')


def get_completed():
    """
    returns list of stellar IDs that have been fit
    """
