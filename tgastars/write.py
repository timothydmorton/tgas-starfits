from __future__ import print_function, division
import os, sys
import numpy as np

from astropy.coordinates import SkyCoord
from astropy import units as u

from isochrones.query import TwoMASS, Tycho2, WISE, EmptyQueryError
from isochrones.extinction import get_AV_infinity
import configobj

from .data import TGAS, dirname, binary_index, get_row, STARMODELDIR
from .query import TGASQuery

def write_ini(i, catalogs=[TwoMASS, Tycho2, WISE], overwrite=False,
                raise_exceptions=False, rootdir=STARMODELDIR):

    # Test to see if this is a binary index.  Return write_binary_ini if it works.
    try:
        i1, i2 = binary_index(i)
        return write_binary_ini(i1, i2, catalogs=catalogs, overwrite=overwrite,
                                raise_exceptions=raise_exceptions, rootdir=rootdir)
    except ValueError:
        pass

    try:
        # name directory by index
        directory = dirname(i, rootdir=rootdir)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        s = get_row(i)

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
                c[n]['id'] = cat.get_id()

        c.write()

    except:
        print('unknown Error with index {}!'.format(i))
        if raise_exceptions:
            raise

def write_binary_ini(i1, i2, catalogs=[TwoMASS, Tycho2, WISE],
                     overwrite=False, raise_exceptions=False, 
                     rootdir=STARMODELDIR):
    """ Write ini file for i1-i2 pair.  

    For this, use just indices so directory names don't get absurdly long
    """
    try:
        if not i1 < i2:
            i1, i2 = i2, i1
        
        s1 = TGAS.iloc[i1]
        s2 = TGAS.iloc[i2]
        
        directory = os.path.join(rootdir, 'binaries', '{}-{}'.format(i1, i2))
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        ini_file = os.path.join(directory, 'stari.ini')
        if os.path.exists(ini_file):
            if overwrite:
                os.remove(ini_file)
            else:
                return
        c = configobj.ConfigObj(ini_file)
        
        # define these coords in epoch=2000
        ra = (s1.ra*u.deg - 15*u.yr*s1.pmra*u.mas/u.yr).to('deg').value
        dec = (s1.dec*u.deg - 15*u.yr*s1.pmdec*u.mas/u.yr).to('deg').value
        coords1 = SkyCoord(ra, dec, unit='deg')
        
        c['ra'] = ra
        c['dec'] = dec
        c['maxAV'] = get_AV_infinity(ra, dec)

        plax1, sig1 = s1.parallax, s1.parallax_error 
        plax2, sig2 = s2.parallax, s2.parallax_error

        # Hack a consistent separation/PA so ObservationTree doesn't get confused
        c1 = SkyCoord(s1.ra, s1.dec, unit='deg')
        c2 = SkyCoord(s2.ra, s2.dec, unit='deg')
        sep = c2.separation(c1).arcsec
        PA = c2.position_angle(c1).deg
        
        norm = 1./sig1**2 + 1./sig2**2
        c['parallax'] = (plax1/sig1**2 + plax2/sig2**2)/norm, 1/np.sqrt(norm)

        q1 = TGASQuery(s1)
        q2 = TGASQuery(s2)
        
        for Cat in catalogs:
            sect = configobj.Section(c, 1, c, {})
            empty = True
            
            cat1 = Cat(q1)
            try: 
                mags = cat1.get_photometry()
                for b in mags:
                    sect[b] = mags[b]
                sect['id'] = cat1.get_id()
                empty = False
            except EmptyQueryError:
                pass
            except ValueError:
                pass
            
            cat2 = Cat(q2)
            try: 
                mags = cat2.get_photometry()
                for b in mags:
                    sect[b + '_1'] = mags[b]
                sect['separation_1'] = sep #cat2.coords.separation(cat1.query_coords).arcsec[0]
                sect['PA_1'] = PA #cat2.coords.position_angle(cat1.query_coords).deg[0]
                sect['id_1'] = cat2.get_id()

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
