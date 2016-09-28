from __future__ import print_function, division
import os, sys
import numpy as np

from astropy.coordinates import SkyCoord
from astropy import units as u

from isochrones.query import TwoMASS, Tycho2, WISE, EmptyQueryError
from isochrones.extinction import get_AV_infinity
import configobj

from .data import TGAS, dirname
from .query import TGASQuery

def write_ini(i, catalogs=[TwoMASS, Tycho2, WISE], overwrite=False,
                raise_exceptions=False):
    try:
        s = TGAS.iloc[i]
        
        # name directory by index
        directory = dirname(i)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        ini_file = os.path.join(directory, 'star.ini')
        if os.path.exists(ini_file):
            if overwrite:
                os.remove(ini_file)
            else:
                return
        c = configobj.ConfigObj(ini_file)
        
        # define these coords in epoch=2000
        ra = (s.ra*u.deg - 15*u.yr*s.pmra*u.mas/u.yr).to('deg').value
        dec = (s.dec*u.deg - 15*u.yr*s.pmdec*u.mas/u.yr).to('deg').value
        coords1 = SkyCoord(ra, dec, unit='deg')
        
        c['ra'] = ra
        c['dec'] = dec
        c['maxAV'] = get_AV_infinity(ra, dec)
        c['parallax'] = s.parallax, s.parallax_error 

        q = TGASQuery(s)
        
        for Cat in catalogs:
            sect = configobj.Section(c, 1, c, {})
            empty = True
            
            cat = Cat(q)
            try: 
                mags = cat.get_photometry()
                for b in mags:
                    sect[b] = mags[b]
                    
                empty = False
            except EmptyQueryError:
                pass
            except ValueError:
                pass

            if not empty:
                n = Cat.name
                c[n] = sect
                c[n]['relative'] = False
                c[n]['resolution'] = 4.

        c.write()

    except:
        print('unknown Error with index {}!'.format(i))
        if raise_exceptions:
            raise

