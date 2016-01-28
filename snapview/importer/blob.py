##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

from ctypes import *


def make_blob(verts, T):
    """ Convert a list of tuples of numbers into a ctypes pointer-to-array.
    """
    size = len(verts) * len(verts[0])
    Blob = T * size
    floats = [c for v in verts for c in v]
    blob = Blob(*floats)
    return cast(blob, POINTER(T))



