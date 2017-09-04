##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import base64

# Cubicweb import
from cubicweb.view import View
from cubicweb.web.views.baseviews import NullView


class DisplayDocumentation(NullView):
    """ Create a view to display the documentation.
    """
    __regid__ = "zeijemol-documentation"
    templatable = True

    def call(self, wave_eid=None, **kwargs):
        """ Create the documentation page.

        Parameters
        ----------
        wave_entity: ste (mandatory)
            a CW 'Wave' entity eid to be documented.
        """
        # Get the parameters
        wave_eid = wave_eid or self._cw.form.get("wave_eid", None)
        wave_rset = self._cw.execute(
            "Any W Where W eid '{0}'".format(wave_eid))
        wave_entity = wave_rset.get_entity(0, 0)

        # Display page content
        self.w(u"<div class='zeijemol-documentation'>")
        self.w(wave_entity.description)
        if wave_entity.filepath is not None:
            with open(wave_entity.filepath, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
            self.w(u'<div id="gallery-img">')
            self.w(
                u'<embed class="gallery-pdf" alt="Embedded PDF" '
                 'src="data:application/pdf;base64, '
                 '{0}" />'.format(encoded_string))
            self.w(u'</div>')
        self.w(u"</div>")

