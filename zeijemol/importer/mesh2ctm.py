##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import os
from ctypes import *
from openctm import *
import polyhedra, blob
import numpy


def octohedron(outdir):
    """ Create a octohedron CTM mesh file.

    Parameters
    ----------
    outdir: str
        directory where a 'octohedron.ctm' file will be saved.
    """
    verts, faces = polyhedra.octohedron() 
    pVerts = blob.make_blob(verts, c_float)
    pFaces = blob.make_blob(faces, c_uint)
    pNormals = POINTER(c_float)()
    ctm = ctmNewContext(CTM_EXPORT)
    ctmDefineMesh(ctm, pVerts, len(verts), pFaces, len(faces), pNormals)
    vertcolors = []
    colors = [(1,1,1,1),
              (1,1,0,1),
              (1,0.5,0,1),
              (0,1,0,1),
              (1,0,0,1),
              (0,0,1,1)]
    vertcolors = [c for c in colors]
    pColors = blob.make_blob(vertcolors, c_float)
    ctmAddAttribMap(ctm, pColors, "Color")
    ctmSave(ctm, os.path.join(outdir, "octohedron.ctm"))
    ctmFreeContext(ctm)


def fsmesh2ctm(fsmesh_file, outdir):
    """ Convert a freesurfer mesh to a CTM mesh.

    Parameters
    ----------
    outdir: str
        directory where a '*.ctm' file will be saved. The output file base
        name will be the same as the input mesh file.
    """
    from clindmri.extensions.freesurfer.reader import TriSurface

    dirname = os.path.dirname(fsmesh_file)
    basename = os.path.basename(fsmesh_file)
    hemi, surf = basename.split(".")
    fsannot_file = os.path.join(dirname, os.pardir, "label",
                                "{0}.aparc.annot".format(hemi))
    surface = TriSurface.load(fsmesh_file, annotfile=fsannot_file)
    colors = []
    for label in surface.labels:
        if label < 0:
            label = 0
        color = numpy.asarray(surface.metadata[label]["color"], dtype=float)
        color /= 255.
        colors.append(tuple(color))
    pVerts = blob.make_blob(surface.vertices, c_float)
    pFaces = blob.make_blob(surface.triangles, c_uint)
    pNormals = POINTER(c_float)()
    pColors = blob.make_blob(colors, c_float)
    ctm = ctmNewContext(CTM_EXPORT)
    ctmDefineMesh(ctm, pVerts, len(surface.vertices), pFaces,
                  len(surface.triangles), pNormals)
    ctmAddAttribMap(ctm, pColors, "Color")
    ctmSave(ctm, os.path.join(outdir, os.path.basename(fsmesh_file) + ".ctm"))
    ctmFreeContext(ctm)  

"""
# Openctm import
from openctm import ctmLoad
from openctm import ctmNewContext
from openctm import CTM_IMPORT
from openctm import CTM_NONE
from openctm import CTM_VERTEX_COUNT
from openctm import CTM_VERTICES
from openctm import CTM_TRIANGLE_COUNT
from openctm import CTM_INDICES
from openctm import ctmGetError
from openctm import ctmGetInteger
from openctm import ctmGetFloatArray
from openctm import ctmGetIntegerArray

# Load the mesh to get metainformation
context = ctmNewContext(CTM_IMPORT)
ctmLoad(context, meshpath)
if ctmGetError(context) == CTM_NONE:
    vert_count = ctmGetInteger(context, CTM_VERTEX_COUNT)
    vertices = ctmGetFloatArray(context, CTM_VERTICES)
    tri_count = ctmGetInteger(context, CTM_TRIANGLE_COUNT)
    indices = ctmGetIntegerArray(context, CTM_INDICES)
else:
    raise ValueError("Can't read '{0}' mesh file.".format(meshpath))
"""

if __name__ == "__main__":
    octohedron(os.getcwd())
    fsmesh2ctm(os.path.join(
        os.getcwd(), "fs", "000000106601", "surf", "rh.white"), os.getcwd())
    fsmesh2ctm(os.path.join(
        os.getcwd(), "fs", "000000106601", "surf", "lh.white"), os.getcwd())
    fsmesh2ctm(os.path.join(
        os.getcwd(), "fs", "000000106601", "surf", "rh.pial"), os.getcwd())
    fsmesh2ctm(os.path.join(
        os.getcwd(), "fs", "000000106601", "surf", "lh.pial"), os.getcwd())


