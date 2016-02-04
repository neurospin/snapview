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

    def call(self, fsdir, header, populationpath):
        """ Create a mesh from a CTM compressed mesh file.

        This procedure expect to find the freesurfer files in the standard
        hierarchy.

        It is possible to press the 'c' key to change the rendering texture.

        Parameters
        ----------
        fsdir: str
            the freesurfer subject base directory: /fsdir/surf/hemi.white -
            /fsdir/stats/hemi.aparc.stats
        header: list of str
            something to display in the viewer overlay.
        populationpath: str
            a path to the population statistics.
        """
        # Build the path to the freesurfer images
        fs_struct = {}
        for hemi in ["rh", "lh"]:
            fs_struct[hemi] = {}
            for surf in ["white", "pial"]:
                fs_struct[hemi][surf] = {
                    "mesh": os.path.join(
                        fsdir, "surf", "{0}.{1}.ctm".format(hemi, surf)),
                    "stats": os.path.join(
                        fsdir, "stats", "{0}.aparc.stats".format(hemi))
                }

        # Construct the data accessor url
        ajaxcallback = self._cw.build_url("ajax", fname="get_ctm_rawdata")

        # Add tool tip
        header += ["Press 'c' to change the texture."]
        logo_link = self._cw.data_url("images/naat_logo.png")
        credit_link = "http://neuroanatomy.github.io/"
        # Create javascript global variables
        jsctmworker = self._cw.data_url("qcsurf/js/CTMWorker.js")
        self.w(u'<script>')
        self.w(u'var meshoverlay="{0}";'.format("<br/>".join(header)))
        self.w(u'var credit_link="{0}";'.format(credit_link))
        self.w(u'var jsctmworker="{0}";'.format(jsctmworker))
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
        self.w(u'<div align="right">')
        self.w(u'<img id="naat" src="{}">'.format(logo_link))
        self.w(u'</div>')

        self.w(u'</div>')
        self.w(u'<div id="overlay"></div>')
        self.w(u'<div id="container"></div>')
        self.w(u'</div>')

        # Initilaize the viewer
        self._cw.add_js("qcsurf/js/qcsurf.js")
        self.w(u'<script>')
        self.w(u'init_gui();')
        self.w(u'population_statistics();')
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
