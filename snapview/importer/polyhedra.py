##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

from math import *


def octohedron():
    """Construct an eight-sided polyhedron.
    """
    f = sqrt(2.0) / 2.0
    verts = [ \
        ( 0, -1,  0),
        (-f,  0,  f),
        ( f,  0,  f),
        ( f,  0, -f),
        (-f,  0, -f),
        ( 0,  1,  0) ]
    faces = [ \
        (0, 2, 1),
        (0, 3, 2),
        (0, 4, 3),
        (0, 1, 4),
        (5, 1, 2),
        (5, 2, 3),
        (5, 3, 4),
        (5, 4, 1) ]
    return verts, faces
