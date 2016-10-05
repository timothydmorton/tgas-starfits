from __future__ import print_function, division

import os
import logging

from isochrones import StarModel
from math import log10, sqrt

from .data import dirname, STARMODELDIR

class GaiaDR1_StarModel(StarModel):

    @property
    def corrected_parallax(self):
        if not hasattr(self, '_corrected_parallax'):
            d = {}
            for s, (val, unc) in self.obs.parallax.items():
                if val < 1.:
                    d[s] = val, sqrt(unc**2 + 0.3**2)
                else:            
                    offset = -0.08 - 0.27*log10(val)
                    d[s] = val - offset, sqrt(unc**2 + 0.3**2)
            self._corrected_parallax = d

        return self._corrected_parallax
    
    def lnlike(p, **kwargs):
        lnl = super(GaiaDR1_StarModel, self).lnlike(p, **kwargs)

        # apply correction for DR1 parallax systematic uncertainty
        pardict = self.obs.p2pardict(p)

        # First, *undo* the parallax lnl, then redo it with systematic correction
        for s,(val,err) in self.obs.parallax.items():
            dist = pardict['{}_0'.format(s)][3]
            mod = 1./dist * 1000.
            
            # Undo base StarModel parallax lnl term
            lnl += 0.5*(val-mod)**2/err**2 

            # Redo with corrected values
            val, err = self.corrected_parallax[s]
            lnl += -0.5*(val-mod)**2/err**2

        return lnl


def get_starmodel(i, modelname='dartmouth_starmodel_single', rootdir=STARMODELDIR):
    d = dirname(i, rootdir=rootdir)
    modfile = os.path.join(d,'{}.h5'.format(modelname))
    logging.debug('loading model from {}'.format(modfile))
    return GaiaDR1_StarModel.load_hdf(modfile)
