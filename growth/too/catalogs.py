import os

from astroquery.vizier import VizierClass
from astropy.table import Table
from celery.local import PromiseProxy
import h5py
import numpy as np
import pkg_resources

from .flask import app


vizier = VizierClass(row_limit=-1)


def add_cl_columns(table):
    # Add dummy 2D and 3D credible level columns.
    # These columns are filled with nans because they are
    # localization dependent.
    table['2D CL'] = np.repeat(np.nan, len(table))
    table['3D CL'] = np.repeat(np.nan, len(table))


def get_from_vizier(*args, **kwargs):
    result, = vizier.query_constraints(*args, **kwargs, cache=True)
    result.convert_bytestring_to_unicode()
    add_cl_columns(result)
    return result


def get_from_package(filename):
    filepath = os.path.join('catalog', filename)
    try:
        f = app.open_instance_resource(filepath)
    except IOError:
        f = pkg_resources.resource_stream(__name__, filepath)
    filepath = f.name
    f.close()
    result = Table(h5py.File(filepath, mode='r'))
    result.convert_bytestring_to_unicode()
    add_cl_columns(result)
    return result


twomass = PromiseProxy(get_from_vizier, ('J/ApJS/199/26/table3',))


galaxies = clu = PromiseProxy(get_from_package, ('CLU.hdf5',))