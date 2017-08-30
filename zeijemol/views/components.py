##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# CW import
from logilab.common.registry import yes
from cubicweb.predicates import anonymous_user
from cubicweb.predicates import match_user_groups
from cubicweb.predicates import authenticated_user
from cubicweb.web import component
from cubicweb.web.views.boxes import SearchBox
from cubicweb.web.views.bookmark import BookmarksBox
from cubicweb.web.views.basecomponents import HeaderComponent
from cubicweb.web.views.basecomponents import AnonUserStatusLink
from cubicweb.web.views.basecomponents import AuthenticatedUserStatus
from logilab.common.decorators import monkeypatch
from cubicweb.web.views.basecontrollers import LogoutController


class SubNavBar(HeaderComponent):
    """ Class that generate a left box on the web browser to access all the
    score waves.

    It will appear on the left and contain the wave names.
    """
    __regid__ = "browse-waves"
    __select__ = authenticated_user()
    order = 1
    context = u"header-menu-left"

    def attributes(self):

        # Sort waves by categories
        rset = self._cw.execute("Any W, C Where W is Wave, W category C")
        struct = {}
        for index, (_, category) in enumerate(rset):
            struct.setdefault(category, []).append(rset.get_entity(index, 0))

        # Get the wave to be displayed
        left_menu = {}
        for category, waves in struct.items():

            # Find unfinished waves
            wave_to_display = []
            for wave_entity in waves:
                wave_name = wave_entity.name
                wave_rset = self._cw.execute(
                    "Any S Where W is Wave, W name '{0}', W snapsets S, "
                    "S scores SC, SC scored_by U, U login '{1}'".format(
                        wave_name, self._cw.session.login))
                snapsets_rset = self._cw.execute(
                    "Any COUNT(S) Where W is Wave, W name '{0}', "
                    "W snapsets S".format(wave_name))
                display_wave_button = True
                if len(wave_rset) != snapsets_rset[0][0]:
                    wave_to_display.append(wave_entity)

            # Display category only if one wave is not finished in this
            # category
            if len(wave_to_display) > 0:

                # Generate a link for each wave to be rated
                for wave_entity in wave_to_display:
                    # > buttons
                    wave_name = wave_entity.name
                    dochref = self._cw.build_url(
                        "view", vid="zeijemol-documentation",
                        wave_eid=wave_entity.eid)
                    title = ("Please help us rating data in '{0}' "
                             "wave ".format(wave_name))
                    title += ("<a href='{0}' target='_blank' data-toggle='tooltip' "
                              "title='Show info'>".format(dochref))
                    title += "<i class='fa fa-info-circle text-primary sr-icons'></i>"
                    title += "</a>"
                    href = self._cw.build_url(
                        "view", vid="gallery-view", wave=wave_name,
                        title=self._cw._(title))
                    left_menu.setdefault(category, []).append([wave_name, href])

        return left_menu 


class HomeButton(HeaderComponent):
    """ Build a home button displayed in the header.
    """
    __regid__ = "home-snapview"
    __select__ = authenticated_user()
    order = 0
    context = u"header-right"

    def attributes(self):
        return self._cw.build_url("view", vid="index"), "Home", "fa-home"


class StatusButton(HeaderComponent):
    """ Build a status button displayed in the header.
    """
    __regid__ = "status-snapview"
    __select__ = authenticated_user()
    order = 1
    context = u"header-right"

    def attributes(self):
        return (self._cw.build_url("view", vid="status-view"), "Show status",
                "fa-pie-chart")


class RatingsButton(HeaderComponent):
    """ Build a ratings button displayed in the header.

    Only the 'managers' have accessed to this functionality.
    """
    __regid__ = "ratings-snapview"
    __select__ = authenticated_user() & match_user_groups("managers")
    order = 2
    context = u"header-right"

    def attributes(self):
        return (self._cw.build_url("view", vid="ratings-view"), "Show ratings",
                "fa-tachometer")


class LogOutButton(AuthenticatedUserStatus):
    """ Close the current session.
    """
    __regid__ = "logout"
    __select__ = authenticated_user()
    order = 3

    def attributes(self):
        return (self._cw.build_url("logout"), "Signout", "fa-sign-out")


@monkeypatch(LogoutController)
def goto_url(self):
    """ In http auth mode, url will be ignored
    In cookie mode redirecting to the index view is enough : either
    anonymous connection is allowed and the page will be displayed or
    we'll be redirected to the login form.
    """
    msg = self._cw._("You have been logged out.")
    return self._cw.base_url()


def registration_callback(vreg):
    vreg.register(RatingsButton)
    vreg.register(SubNavBar)
    vreg.register(HomeButton)
    vreg.register(StatusButton)
    vreg.register(LogOutButton)
    vreg.unregister(BookmarksBox)
    vreg.unregister(SearchBox)
    vreg.unregister(AnonUserStatusLink)
    vreg.unregister(AuthenticatedUserStatus)
