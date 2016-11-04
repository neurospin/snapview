##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


# System import
import base64
import json
import os
from PIL import Image

# CW import
from cubicweb.view import View
from cubicweb.web.views.ajaxcontroller import ajaxfunc


class TriplanarView(View):
    """ Dynamic volume slicer from 'coronal', 'axial' and 'sagittal' stacks.
    """
    __regid__ = "triplanar-view"
    templatable = False
    # This message will be formated with the snap eid
    error_message = ("Triplanar view not responding. Please contact the "
                     "service administrator specifying the the snap code "
                     "'{0}'.")

    def call(self): #, snap_eid, file_data, data_type):
        """ Create the viewer: orign is at the bottom left corner of the image,
        thus the stack ordering must be:
        axial: I->S
        coronal: P->A
        sagittal: L->R

        Depending on your data, the loading time can be quite important, thus
        all the button with a 'triview-btn' class will be disabled during
        this step.

        The code can display a single, two or three orientations view.

        Parameters
        ----------
        snap_eid: Entity (mandatory)
            the snap CW entity eid.
        file_data: dict (mandatory)
            the 'coronal', 'axial' and 'sagittal' stack names as keys with
            a list of ordered image files as value.
        data_type: str (mandatory)
            the image to display extension.
        """
        # Define parameters
        snap_eid = self._cw.form["snap_eid"]
        file_data = json.loads(self._cw.form["file_data"])
        data_type = self._cw.form["data_type"]
        error = self.error_message.format(snap_eid)
        brightness = 100

        # Add JS and CSS resources for the sliders and triview
        self.w(u'<script type="text/javascript" '
                'src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/'
                'jquery.min.js"></script>')
        for path in ("triview/js/simple-slider.min.js",
                     "triview/js/triview.js"):
            href = self._cw.data_url(path)
            self.w(u'<script type="text/javascript" src="{0}"></script>'.format(href))
        for path in ("triview/css/simple-slider-volume.css",
                     "triview/css/triview.css"):
            href = self._cw.data_url(path)
            self.w(u'<link type="text/css" rel="stylesheet" href="{0}">'.format(href))

        # Check inputs
        orientations = ["sagittal", "coronal", "axial"]
        shapes = {}
        nb_slices = {}
        for orient in file_data:
            # > check orientation
            if orient not in orientations:
                self.w(u"<h1>{0}</h1>".format(error))
                self.w(u"<script>")
                self.w(u"disableTriViewBtn();")
                self.w(u"</script>")
                return
            # > check image sizes
            stack_size = None
            nb_slices[orient] = len(file_data[orient]) - 1
            for path in file_data[orient]:
                with Image.open(path) as open_image:
                    if stack_size is None:
                        stack_size = open_image.size
                        shapes[orient] = stack_size
                    elif stack_size != open_image.size:
                        self.w(u"<h1>{0}</h1>".format(error))
                        self.w(u"<script>")
                        self.w(u"disableTriViewBtn();")
                        self.w(u"</script>")
                        return

        # Add an hidden loading image
        html = "<div id='loading-msg' style='display: none;' align='center'>"
        loading_img_url = self._cw.data_url("triview/load.gif")
        html += "<img src='{0}'/>".format(loading_img_url)
        html += "</div>"

        # Add viewer containers
        html += "<div class='container'>"
        # > create the brightness horizontal scroll bar
        html += "<div>"
        html += "<h4 style='color: white;'>BRIGHTNESS</h4>"
        html += ("<input id='brightness-bar' type='text' "
                 "data-slider='true' data-slider-range='0,200' "
                 "value='100' data-slider-step='1' "
                 "data-slider-highlight='true' "
                 "data-slider-theme='volume'>")
        html += ("<p id='brightness-bar-text' style='color: "
                 "white;margin-bottom: 50px;'>{0} %</p>".format(brightness))
        html += "</div>"
        # > create image containers
        for orient, shape in shapes.items():
            html += "<div id='{0}' class='subdiv'>".format(orient)
            html += "<h4 style='color: white;'>{0}</h4>".format(
                orient.upper())
            html += ("<input class='slice-bar' type='text' data-slider='true' "
                     "data-slider-range='0,{0}' value='{1}' "
                     "data-slider-step='1' data-slider-highlight='true' "
                     "data-slider-theme='volume'>".format(
                         nb_slices[orient], nb_slices[orient] // 2))
            html += ("<p class='slice-bar-text' style='color: white;'>"
                     "{0} / {1}</p>".format(
                         nb_slices[orient] // 2, nb_slices[orient]))
            html += ("<canvas class='slice-img' width='{0}' height='{1}'>"
                     "</canvas>".format(shape[0], shape[1]))
            html += "</div>"
        html += "</div>"

        # Construct the data accessor url
        ajaxcallback = self._cw.build_url("ajax", fname="get_b64_images")

        # Create javascript global variables
        triview_data = {
            "dtype": data_type.lower(),
            "file_data": file_data,
            "ajaxcallback": ajaxcallback,
            "orientations": file_data.keys(),
            "brightness": 100,
            "shapes": shapes,
            "nb_slices": nb_slices}
        html += "<script>"
        html += "var triview_data = {0};".format(json.dumps(triview_data))
        html += "</script>"

        # Initilaize the viewer
        html += "<script>"
        html += "$(document).ready(function() {"
        html += "disableTriViewBtn();"
        html += "initTriViewGui();"
        html += "});"
        html += "</script>"

        # Set page code
        self.w(unicode(html))


@ajaxfunc(output_type="json")
def get_b64_images(self):
    """ Ajax callback used to load images in the 'file_data' form in base64.
    """
    file_data = json.loads(self._cw.form["file_data"])
    output = {}
    for orient, fpaths in file_data.items():
        encoded_images = []
        for path in fpaths:
            with open(path, "rb") as open_image:
                encoded_image = base64.b64encode(open_image.read())
                encoded_images.append(encoded_image)
        output[orient] = encoded_images
    return output
