##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import division
import base64
import json
import os

# Cubicweb import
from cubicweb.web.views.ajaxcontroller import ajaxfunc
from cubicweb.view import View


class QcSurf(View):
    """ Create a mesh rendering using Three (WebGL).
    """
    __regid__ = "mesh-qcsurf"
    div_id = "mesh-qcsurf"
    naat_url = "http://neuroanatomy.github.io/"

    def call(self, filepaths, header, populationpath):
        """ Create a mesh from a CTM compressed mesh file.

        This procedure expect to find the freesurfer files in the standard
        hierarchy.

        It is possible to press the 'c' key to change the rendering texture.

        Parameters
        ----------
        filepaths: list of str
            the path to the FreeSurfer surface and stat files:
            /fsdir/surf/<hemi>.white -
            /fsdir/surf/<hemi>.pial -
            /fsdir/stats/<hemi>.aparc.stats
            Six files are expected.
        header: list of str
            something to display in the viewer overlay.
        populationpath: str
            a path to the population statistics.
        """
        # Check inputs
        if len(filepaths) != 6:
            raise ValueError("Fatal Error: six files are expected "
                             "'{0}'.".format(header))

        # Build the path to the freesurfer images
        fs_struct = {}
        for hemi in ["rh", "lh"]:
            fs_struct[hemi] = {}
            for surf in ["white", "pial"]:
                surffiles = [path for path in filepaths
                             if hemi in path and surf in path]
                statsfiles = [path for path in filepaths
                              if hemi in path and "stats" in path]
                for struct in (surffiles, statsfiles):
                    if len(struct) != 1:
                        raise ValueError(
                            "Fatal Error: one surface and one stat file "
                            "expected '{0}'.".format(header))
                fs_struct[hemi][surf] = {
                    "mesh": surffiles[0],
                    "stats": statsfiles[0]
                }

        # Load the population statistic
        with open(populationpath, "r") as open_file:
            population_stats = json.load(open_file)

        # Construct the data accessor url
        ajaxcallback = self._cw.build_url("ajax", fname="get_ctm_rawdata")

        # Add tool tip
        header += ["Press 'c' to change the texture."]       

        # Create javascript global variables
        naat_logo_url = self._cw.data_url("images/naat_logo.png")
        jsctmworker = self._cw.data_url("qcsurf/js/CTMWorker.js")
        self.w(u'<script>')
        self.w(u'var meshoverlay="{0}";'.format("<br/>".join(header)))
        self.w(u'var jsctmworker="{0}";'.format(jsctmworker))
        self.w(u'var pop_stats={0};'.format(json.dumps(population_stats)))
        self.w(u'var populationpath="{0}";'.format(populationpath))
        self.w(u'var ajaxcallback="{0}";'.format(ajaxcallback))
        self.w(u'var fs_struct={0};'.format(json.dumps(fs_struct)))
        self.w(u'var hemi="rh";')
        self.w(u'var surf="white";')
        self.w(u'</script>')

        # Add css resources
        self._cw.add_css("qcsurf/css/style.css")

        # Add js resources
        #self._cw.add_js("qcsurf/js/jquery-1.11.0.min.js")
        self._cw.add_js("qcsurf/js/three.min.js")
        self._cw.add_js("qcsurf/js/TrackballControls.js")
        self._cw.add_js("qcsurf/js/lzma.js")
        self._cw.add_js("qcsurf/js/ctm.js")
        self._cw.add_js("qcsurf/js/CTMLoader.js")

        # Add viewer containers
        self.w(u'<div id="text"></div>')
        self.w(u'<div id="viewer">')
        self.w(u'<div id="toolbar">')
        self.w(u'<span id="hemisphere" class="select"> '
               '<span id="lh" class="button">Left</span> '
               '<span id="rh" class="button selected">Right</span></span>')
        self.w(u'<span id="surface" class="select"> '
               '<span id="pial" class="button">Pial</span> '
               '<span id="white" class="button selected">White</span></span>')
        self.w(u'<span id="naat"><a href="{1}" target="_blank"><img '
                'class="button" src="{0}"></a></span>'.format(
                    naat_logo_url, self.naat_url))
        self.w(u'</div>')
        self.w(u'<div id="overlay"></div>')
        self.w(u'<div id="container"></div>')
        self.w(u'</div>')

        # Initilaize the viewer
        self._cw.add_js("qcsurf/js/qcsurf.js")
        self.w(u'<script>')
        self.w(u'init_gui();')
        self.w(u'init_3d();')
        self.w(u'get_new_data();')
        self.w(u'animate();')
        self.w(u'</script>')


@ajaxfunc(output_type="json")
def get_ctm_rawdata(self):
    """ Get CTM raw data.

    Parameters
    ----------
    ctmfile: str
        the ctm file path.
    statsfile: str
        the stats file path.

    Returns
    -------
    data: dict
        the raw data are associated to the 'encoded_mesh' key, and the stats
        to the 'statlines' key.
    """
    # Get parameters
    ctmfile = self._cw.form["ctmfile"]
    statsfile = self._cw.form["statsfile"]

    # Encode the mesh binary buffer that will be decoded in the CTMLoader.
    with open(ctmfile, "rb") as open_file:
        encoded_mesh = base64.b64encode(open_file.read())

    # Load the stats file
    with open(statsfile) as open_file:
        statlines = open_file.readlines()

    # Format the ajax data
    data = {"encoded_mesh": encoded_mesh, "statlines": statlines}

    return data
