from __future__ import print_function, division

import os, sys, re
import numpy as np
import pandas as pd
import logging
from multiprocessing import Pool

from .data import get_completed_ids, DATADIR, STARMODELDIR, source_id
from .models import get_starmodel

def get_quantiles(i, columns=['mass','age','feh','distance','AV'],
                 qs=[0.05,0.16,0.5,0.84,0.95], modelname='mist_starmodel_single',
                 verbose=False, raise_exceptions=False, rootdir=STARMODELDIR):
    """Returns parameter quantiles for starmodel i (as indexed by TGAS table)
    """
    try:
        mod = get_starmodel(i, rootdir=rootdir)
    except:
        if verbose:
            print('cannnot load {}'.format(modfile))
        if raise_exceptions:
            raise
        return pd.DataFrame()
    
    # Get actual column names
    true_cols = []
    for c1 in mod.samples.columns:
        for c2 in columns:
            if re.search(c2, c1):
                true_cols.append(c1)

    q_df = mod.samples[true_cols].quantile(qs)
    # new_cols = []
    # new_col_base = {}
    # for c in true_cols:
    #     if not re.search('mass',c):
    #         newc = c[:-2]
    #     else:
    #         newc = 'mass' + c[-2:]
    #     new_col_base[c] = newc
    #     for q in qs:
    #         new_cols.append('{}_{:02.0f}'.format(newc,q*100))

    #ix = os.path.basename(d)
    # df = pd.DataFrame(columns=new_cols, index=[i])
    df = pd.DataFrame(index=[i])

    for c in true_cols:
        for q in qs:
            # col = new_col_base[c] + '_{:02.0f}'.format(q*100)
            col = c + '_{:02.0f}'.format(q*100)
            df.ix[i, col] = q_df.ix[q, c]
        
    return df

class quantile_worker(object):
    def __init__(self, id_list, **kwargs):
        self.id_list = id_list
        self.kwargs = kwargs

    def __call__(self, i):
        return get_quantiles(id_list[i], **self.kwargs)

def make_summary_df(ids=None, processes=1, filename=None, **kwargs):

    if ids is None:
        ids = get_completed_ids()

    pool = Pool(processes=processes)
    worker = quantile_worker(id_list=ids, **kwargs)
    dfs = pool.map(worker, xrange(len(ids)))

    df = pd.concat(dfs)
    if filename is None:
        filename = os.path.join(DATADIR, 'summary.h5')
    df.to_hdf(filename, 'df')

    print('Summary dataframe written to {}'.format(filename))
    return df
