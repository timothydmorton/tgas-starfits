from __future__ import print_function, division

from isochrones import StarModel

from .data import dirname

def get_starmodel(i, modelname='dartmouth_starmodel_single'):
    d = dirname(i)

    modfile = os.path.join(d,'{}.h5'.format(modelname))
    return StarModel.load_hdf(modfile)
