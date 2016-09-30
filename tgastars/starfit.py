from __future__ import print_function, division

from isochrones.starfit import starfit

from .data import dirname
from .models import GaiaDR1_StarModel

def tgas_starfit(i, **kwargs):
    d = dirname(i)
    return starfit(d, starmodel_type=GaiaDR1_StarModel, **kwargs)


