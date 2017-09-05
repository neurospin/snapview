##########################################################################
# NSAp - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import division
import os
import collections

# Cubicweb import
from cubicweb import _
from cubicweb.web.views.startup import IndexView
from cubicweb.web.httpcache import NoHTTPCacheManager
from cubicweb.view import View
from cubicweb.predicates import authenticated_user
from cubicweb.predicates import match_user_groups


class ZEIJEMOLNotRaterIndexView(IndexView):
    """ Class that defines the index view.
    """
    __regid__ = "index"
    __select__ = authenticated_user() & ~match_user_groups(
        "managers", "moderators")
    title = _("Index")

    def call(self, **kwargs):
        """ Create the loggedin 'index' page of our site.
        """
        # Format template
        template = self._cw.vreg.template_env.get_template("startup.logged.jinja2")
        html = template.render(
            header_url=self._cw.data_url("creative/img/neurospin.jpg"),
            moderator=False,
            waves_progress={})
        self.w(html)


class ZEIJEMOLRaterIndexView(IndexView):
    """ Class that defines the index view.
    """
    __regid__ = "index"
    __select__ = authenticated_user() & match_user_groups(
        "managers", "moderators")
    title = _("Index")
    http_cache_manager = NoHTTPCacheManager

    def call(self, **kwargs):
        """ Create the loggedin 'index' page of our site.
        """
        # Get information to display a summary table with one progress bar
        # for each wave
        rset = self._cw.execute(
            "Any S, W, N, C Where S is SnapSet, S wave W, W name N, "
            "W category C")
        struct = {}
        for index, row in enumerate(rset):
            wave_name = row[2]
            category = row[3]
            struct.setdefault(category, {}).setdefault(wave_name, []).append(
                rset.get_entity(index, 0))
        waves_progress = {}
        for category, wave_struct in struct.items():
            for wave_name, snapset in wave_struct.items():
                nb_of_snapset= len(snapset)
                nb_rates = 0
                for entity in snapset:
                    scores = [
                        e for e in entity.scores
                        if e.scored_by[0].login == self._cw.session.login]
                    if len(scores) == 1:
                        nb_rates += 1
                    elif len(scores) > 1:
                        raise Exception(
                            "We expect one score per user for one snap.")
                waves_progress.setdefault(category, []).append(
                    (wave_name, int(nb_rates / nb_of_snapset * 100)))

        # Format template
        template = self._cw.vreg.template_env.get_template("startup.logged.jinja2")
        html = template.render(
            header_url=self._cw.data_url("creative/img/neurospin.jpg"),
            moderator=True,
            waves_progress=waves_progress)
        self.w(html)


class ZEIJEMOLIndexView(IndexView):
    """ Class that defines the index view.
    """
    __regid__ = "index"
    __select__ = ~authenticated_user()
    title = _("Index")
    templatable = False
    default_message = "Unable to locate the startup page."

    def call(self, **kwargs):
        """ Create the anonymous 'index' page of our site.
        """
        # Get additional resources links
        css = []
        for path in ("creative/vendor/bootstrap/css/bootstrap.min.css",
                     "creative/vendor/font-awesome/css/font-awesome.min.css",
                     "creative/vendor/magnific-popup/magnific-popup.css",
                     "creative/css/creative.css"):
            css.append(self._cw.data_url(path))
        js = []
        for path in ("creative/vendor/jquery/jquery.min.js",
                     "creative/vendor/bootstrap/js/bootstrap.min.js",
                     "creative/vendor/scrollreveal/scrollreveal.min.js",
                     "creative/vendor/magnific-popup/jquery.magnific-popup.min.js",
                     "creative/js/creative.js"):
            js.append(self._cw.data_url(path))

        # Format template
        template = self._cw.vreg.template_env.get_template("startup.jinja2")
        html = template.render(
            header_url=self._cw.data_url("creative/img/neurospin.jpg"),
            login_url=self._cw.build_url(
                "login", __message=u"Please login with your account."),
            contact_email=self._cw.vreg.config.get(
                "administrator-emails", "noreply@cea.fr"),
            css_url=css,
            js_url=js)
        self.w(html)


class PieChart(View):
    """ Create a pie chart representing the user rates with HighCharts.
    """
    __regid__ = "pie-highcharts"
    paginable = False
    div_id = "pie-highcharts"

    def call(self, data, title, container_id=0,
             highcharts_js="https://code.highcharts.com/highcharts.js",
             exporting_js="https://code.highcharts.com/modules/exporting.js"):
        """ Method that will create a pie chart from the user rates.

        Parameters
        ----------
        data: dict
            a dictionnary with title as keys and occurence (in percent) as
            values.
        title: str
            a title for the chart.
        container_id: int
            an identifier for the chart container.
        """
        # Add js resources
        self._cw.add_js(highcharts_js, localfile=False)
        self._cw.add_js(exporting_js, localfile=False)

        # Create the highcharts string representation of the data
        sdata = '['
        for key, value in data.items():
            sdata += '["{0}", {1}], '.format(key, value)
        sdata += ']'

        # Generate the script
        # > headers
        self.w(u'<script type="text/javascript">')
        self.w(u'$(function () {{ $("#hc_container_{0}").highcharts({{'.format(
            container_id))
        # > configure credit
        self.w(u'credits : {enabled : false}, ')
        # > configure chart
        self.w(u'chart: {plotBackgroundColor: null, plotBorderWidth: 1, '
               'plotShadow: false}, ')
        # > configure title
        self.w(u'title: {{text: "{0}"}}, '.format(title))
        # > configure tooltip
        self.w(u'tooltip: {pointFormat: "{series.name}: '
               '<b>{point.percentage:.1f}%</b>" }, ')
        # > configure plot
        self.w(u'plotOptions: {')
        self.w(u'pie: {allowPointSelect: true, cursor: "pointer", '
               'dataLabels: { enabled: true, format: "<b>{point.name}</b>: '
               '{point.percentage:.1f} %", style: {color: (Highcharts.theme '
               '&& Highcharts.theme.contrastTextColor) || "black"}}}')
        self.w(u'}, ')
        # > configure series
        self.w(u'series: [{{type: "pie", name: "Rate", '
               'data: {0}}}] '.format(sdata))
        # > close headers
        self.w(u'}); ')
        self.w(u'}); ')
        self.w(u'</script>')

        # Add a container in the body to display the pie chart
        self.w(u'<div id="hc_container_{0}" class="hc_container">'
               '</div>'.format(container_id))


def registration_callback(vreg):
    #vreg.register_and_replace(SnapIndexView, IndexView)
    vreg.register_and_replace(ZEIJEMOLIndexView, IndexView)
    vreg.register(ZEIJEMOLRaterIndexView)
    vreg.register(ZEIJEMOLNotRaterIndexView)
    vreg.register(PieChart)
