from __future__ import print_function, division

import os, sys, re
import numpy as np
import pandas as pd
from multiprocessing import Pool

from isochrones import StarModel
from .data import dirname, get_completed_ids, DATADIR

def get_quantiles(i, columns=['mass_0_0','age_0','feh_0','distance_0','AV_0'],
                 qs=[0.05,0.16,0.5,0.84,0.95], model_name='dartmouth_starmodel_single',
                 verbose=False, raise_exceptions=False):
    """Returns parameter quantiles for starmodel i (as indexed by TGAS table)
    """


    d = dirname(i)

    modfile = os.path.join(d,'{}.h5'.format(model_name))
    try:
        mod = StarModel.load_hdf(modfile)
    except:
        if verbose:
            print('cannnot load {}'.format(modfile))
        if raise_exceptions:
            raise
        return pd.DataFrame()
        
    q_df = mod.samples[columns].quantile(qs)
    new_cols = []
    new_col_base = {}
    for c in columns:
        if not re.search('mass',c):
            newc = c[:-2]
        else:
            newc = 'mass' + c[-2:]
        new_col_base[c] = newc
        for q in qs:
            new_cols.append('{}_{:02.0f}'.format(newc,q*100))

    ix = os.path.basename(d)
    df = pd.DataFrame(columns=new_cols, index=[ix])
    
    for c in columns:
        for q in qs:
            col = new_col_base[c] + '_{:02.0f}'.format(q*100)
            df.ix[ix, col] = q_df.ix[q, c]
        
    return df

def make_summary_df(processes=1, **kwargs):

    pool = Pool(processes=processes)
    dfs = pool.map(get_quantiles, get_completed_ids())

    df = pd.concat(dfs)
    df.to_hdf(os.path.join(DATADIR, 'summary.h5'), 'df')

    return df
