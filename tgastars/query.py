
from __future__ import print_function, division

import pandas as pd
import numpy as np
from isochrones.query import Query

from .data import TGASPATH

TGAS = None

class TGASQuery(Query):
    """Special subclass for a query based on TGAS DR1.  

    `row` is a row of the Gaia DR1 table.
    """
    def __init__(self, row, radius=5):
        self.row = row
        Query.__init__(self, row.ra, row.dec, row.pmra, row.pmdec, 
                        epoch=row.ref_epoch, radius=radius)

    @classmethod
    def from_id(cls, i, **kwargs):
        global TGAS
        if TGAS is None:
            TGAS = pd.read_hdf(TGASPATH, 'df')
        if i < len(TGAS):
            ind = i
        else:            
            ind = np.where(TGAS.source_id.astype(int)==i)[0][0]
        new = cls(TGAS.iloc[ind], **kwargs)
        return new