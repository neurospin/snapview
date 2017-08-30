##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# Cubicweb import
from cubicweb.web.views.basetemplates import HTMLPageFooter
from cubicweb.web.views.basetemplates import HTMLPageHeader
from cubicweb.web.views.wdoc import HelpAction
from cubicweb.web.views.wdoc import AboutAction
from cubicweb.web.views.actions import PoweredByAction
from cubicweb.web.views.basecomponents import ApplLogo
from logilab.common.registry import yes


###############################################################################
# ACTIONS
###############################################################################


class ZEIJEMOLPageFooter(HTMLPageFooter):
    __regid__ = "footer"
    title = u"Footer"

    def footer_content(self):
        template = self._cw.vreg.template_env.get_template("footer.jinja2")
        html = template.render(
            contact_email=self._cw.vreg.config.get(
                "administrator-emails", "noreply@cea.fr"))
        self.w(html)


class ZEIJEMOLPageHeader(HTMLPageHeader):
    __regid__ = "header"
    title = u"Header"

    def main_header(self, view):
        """ build the top menu with authentification info and the rql box.
        """
        # Get additional information
        components = self._cw.vreg["ctxcomponents"].poss_visible_objects(
            self._cw, rset=self.cw_rset, view=view, context="header-menu-left")
        assert len(components) == 1
        left_menu = components[0].attributes()

        icons = []
        for colid, context in self.headers:
            components = self._cw.vreg["ctxcomponents"].poss_visible_objects(
                self._cw, rset=self.cw_rset, view=view, context=context)
            for comp in components:
                if hasattr(comp, "attributes"):
                    icons.append(comp.attributes())

        # Format template
        template = self._cw.vreg.template_env.get_template("header.jinja2")
        html = template.render(
            left_menu=left_menu,
            right_icons=icons)
        self.w(html)


def registration_callback(vreg):

    # Update the footer
    vreg.register_and_replace(ZEIJEMOLPageFooter, HTMLPageFooter)
    vreg.register_and_replace(ZEIJEMOLPageHeader, HTMLPageHeader)
    vreg.unregister(HelpAction)
    vreg.unregister(AboutAction)
    vreg.unregister(PoweredByAction)
    vreg.unregister(ApplLogo)
