
from __future__ import print_function, division

from isochrones.query import Query

class TGASQuery(Query):
    """Special subclass for a query based on TGAS DR1.  

    `row` is a row of the Gaia DR1 table.
    """
    def __init__(self, row, radius=5):
        self.row = row
        Query.__init__(self, row.ra, row.dec, row.pmra, row.pmdec, 
                        epoch=row.ref_epoch, radius=radius)

