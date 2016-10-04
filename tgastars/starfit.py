from __future__ import print_function, division

import os

from isochrones.starfit import starfit

from .data import dirname
from .models import GaiaDR1_StarModel
from .write import write_ini

def tgas_starfit(i, write_ini=True, ini_kwargs=None, rootdir=STARMODELDIR,
                    **kwargs):
    d = dirname(i, rootdir=rootdir)
    if not os.path.exists(os.path.join(d, 'star.ini')):
        if not write_ini:
            raise ValueError('star.ini not written for {}'.format(i))
        if ini_kwargs is None:
            ini_kwargs = {}
            if 'raise_exceptions' not in ini_kwargs:
                ini_kwargs['raise_exceptions'] = True
        write_ini(i, **ini_kwargs)

    return starfit(d, starmodel_type=GaiaDR1_StarModel, **kwargs)


