from __future__ import print_function, division

import os

from isochrones import StarModel
from math import log10, sqrt

from .data import dirname

class GaiaDR1_StarModel(StarModel):

    def _corrected_parallax(self, val, unc):
        """ Returns new value and uncertainty for parallax, given systematic correction

        According to http://arxiv.org/abs/1609.05390
        """
        # For small parallaxes, no offest, just systematic error term
        if val < 1.:
            return val, sqrt(unc**2 + 0.3**2)
        else:            
            offset = -0.08 - 0.27*log10(val)
            return val - offset, sqrt(unc**2 + 0.3**2)

    def lnlike(p, **kwargs):
        lnl = super(GaiaDR1_StarModel, self).lnlike(p, **kwargs)

        # apply correction for DR1 parallax systematic uncertainty
        pardict = self.obs.p2pardict(p)

        # First, *undo* the parallax lnl, then redo it with systematic correction
        for s,(val,err) in self.obs.parallax.items():
            dist = pardict['{}_0'.format(s)][3]
            mod = 1./dist * 1000.
            lnl += 0.5*(val-mod)**2/err**2 #undoing base StarModel parallax lnl

            val, err = self._corrected_parallax(val, err)
            lnl += -0.5*(val-mod)**2/err**2



def get_starmodel(i, modelname='dartmouth_starmodel_single'):
    d = dirname(i)

    modfile = os.path.join(d,'{}.h5'.format(modelname))
    return GaiaDR1_StarModel.load_hdf(modfile)
