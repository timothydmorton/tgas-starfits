from __future__ import print_function, division

from isochrones.starfit import starfit

from .data import dirname
from .models import GaiaDR1_StarModel
from .write import write_ini

def tgas_starfit(i, ini_kwargs, **kwargs):
    d = dirname(i)
    if not os.path.exists(os.path.join(d, 'star.ini')):
        write_ini(i, **ini_kwargs)
        
    return starfit(d, starmodel_type=GaiaDR1_StarModel, **kwargs)


