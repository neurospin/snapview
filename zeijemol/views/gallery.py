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
import numpy
from numpy.random import choice

# CW import
from cgi import parse_qs
from cubicweb.view import View
import cubes.zeijemol as zeijemol


class Gallery(View):
    """ Custom view to score snap files.
    """
    __regid__ = "gallery-view"
    extra_answers_description = u"Justify rating"
    allowed_viewers = ("FILE", "SURF", "TRIPLANAR")

    def call(self, **kwargs):
        """ Create the rate form.
        """
        # Get some parameters
        path = self._cw.relative_path()
        if "?" in path:
            path, param = path.split("?", 1)
            kwargs.update(parse_qs(param))
        title = kwargs["title"][0]
        wave_name = kwargs["wave"][0]

        # Add script to resize iframe as content
        #self._cw.add_js("triview/js/resize-iframe.js")

        # Get the wave extra answers
        rset = self._cw.execute("Any E Where W is Wave, W name '{0}', "
                                "W extra_answers E".format(wave_name))
        extra_answers = json.loads(rset[0][0])

        # Select the snapset to be rated: use the internal connection in order
        # to get the full rating distribution and then intersect this
        # distribution with the user rates in order to uniformally
        # fill the database
        # Note: need to access the selected snapset with the user rights
        # because the internal session is closed after with ...:
        with self._cw.cnx._cnx.repo.internal_cnx() as cnx:
            rset = cnx.execute("Any S Where W is Wave, W name '{0}', "
                               "W snapsets S".format(wave_name))
            # > find the user ratings and the all user ratings distribution
            nb_scores = []
            nb_user_scores = []
            for index in range(rset.rowcount):
                entity = rset.get_entity(index, 0)
                scores = entity.scores
                nb_scores.append(len(scores))
                nb_user_scores.append(
                    len([sc for sc in scores
                        if sc.scored_by[0].login == self._cw.session.login]))
            nb_scores = numpy.asarray(nb_scores).astype(numpy.single)
            nb_user_scores = numpy.asarray(nb_user_scores)
            # > check that the user has something to rate
            if nb_user_scores.min() == 1:
                error = "No more snap to rate, thanks."
                self.w(u"<h1>{0}</h1>".format(error))
                return
            # > compute a sampling distribution
            # p(snapset|len(snapset_scores)=X) = 1/(X + 1) (before norm)
            # p(snapset) = 1./(X * Nx) where Nx= number of snapsets with
            # X scores (rated X times)
            keys, counts = numpy.unique(nb_scores, return_counts=True)
            item_per_score = dict(zip(keys, counts))
            weights = [1. / ((x + 1) * item_per_score[x]) for x in nb_scores]
            weights = numpy.asarray(weights).astype(numpy.single)
            # > set a null probability for already rated snapsets
            weights[numpy.where(nb_user_scores == 1)] = 0
            # > normalize the distribution
            weights = weights / sum(weights)
            # > weighted pick
            snapset_index = choice(range(len(weights)), p=weights)
            snapset_eid = rset[snapset_index][0]
        rset = self._cw.execute("Any S Where S eid '{0}'".format(snapset_eid))
        snapset_entity = rset.get_entity(0, 0)

        # Display title
        self.w(u'<h1>{0}</h1>'.format(title))

        # Dispaly status
        nb_of_snapsets = len(nb_scores)
        nb_snapsets_to_rate = numpy.sum(1 - nb_user_scores)
        progress = int((1 - nb_snapsets_to_rate / nb_of_snapsets) * 100)
        self.w(u'<div class="progress">')
        self.w(u'<div class="progress-bar" role="progressbar" '
               'aria-valuenow="{0}" aria-valuemin="0" aria-valuemax='
               '"100" style="width:{0}%">'.format(progress))
        self.w(u'{0}%'.format(progress))
        self.w(u'</div>')
        self.w(u"</div>")

        # Display/send a form
        href = self._cw.build_url("rate-controller", eid=snapset_entity.eid,
                                  wave_name=wave_name)
        wave_entity = snapset_entity.wave[0]
        score_definitions = json.loads(wave_entity.score_definitions)
        form_html = []
        form_html.append(u'<div id="gallery-form">')
        form_html.append(u'<form action="{0}" method="post">'.format(href))
        for definition in score_definitions:
            form_html.append(
                u'<input class="btn btn-success triview-btn" type="submit" '
                 'name="rate" value="{0}"/>'.format(definition))
        form_html.append(
            u'<input class="btn btn-info triview-btn" type="submit" '
             'name="rate" value="Rate later"/>')
        if len(extra_answers) > 0:
            form_html.append(u'<br/><br/>')
            form_html.append(u'<u>{0}:</u>'.format(
                self.extra_answers_description))
        for extra in extra_answers:
            form_html.append(u'<div class="checkbox">')
            form_html.append(u'<label>')
            form_html.append(u'<input class="checkbox" type="checkbox" '
                              'name="extra_answers" value="{0}"/>'.format(
                                    extra))
            form_html.append(unicode(extra))
            form_html.append(u'</label>')
            form_html.append(u'</div>')
        form_html.append(u'</form>')
        form_html.append(u'</div>')

        # Check that all the viewers are declared
        in_error = False
        for snap_entity in snapset_entity.snaps:
            if snap_entity.viewer not in self.allowed_viewers:
                error = ("Can't find the appropriate viewer. Please contact "
                         "the service administrator specifying the '{0}' "
                         "wave viewer '{1}' is not responding "
                         "on '{2}'.".format(wave_entity.name,
                                            snap_entity.viewer,
                                            self._cw.base_url()))
                self.w(u"<h1>{0}</h1>".format(error))
                in_error = True

        # Display all the declared snaps for this snapset
        if not in_error:
            # > render form
            self.w("\n".join(form_html))
            for snap_entity in snapset_entity.snaps:
                # > get external files
                filepaths = [e.filepath for e in snap_entity.files]
                # > display the files
                if snap_entity.viewer == "FILE":
                    if len(filepaths) != 1:
                        raise ValueError(
                            "Fatal Error: check system integrity "
                            "'{0}'.".format(snap_entity.identifier))
                    dtype = snap_entity.files[0].dtype
                    with open(filepaths[0], "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    self.w(u'<div id="gallery-img">')
                    if dtype.lower() == "pdf":
                        self.w(
                            u'<embed class="gallery-pdf" alt="Embedded PDF" '
                             'src="data:application/pdf;base64, '
                             '{0}" />'.format(encoded_string))
                    else:
                        self.w(
                            u'<img class="gallery-img" alt="Embedded Image" '
                             'src="data:image/{0};base64, {1}" />'.format(
                                   dtype.lower(), encoded_string))
                    self.w(u'</div>')
                # > display the files in a triplanar view
                elif snap_entity.viewer == "TRIPLANAR":
                    file_data = {}
                    for e in snap_entity.files:
                        file_data.setdefault(e.description, []).append(
                            (e.order, e.filepath, e.dtype))
                    data_type = None
                    for key in file_data.keys():
                        if data_type is None:
                            data_type = file_data[key][0][2]
                        file_data[key] = [
                            elem[1] for elem in sorted(file_data[key],
                                                       key=lambda x: x[0])]
                    href = self._cw.build_url(
                        vid="triplanar-view", snap_eid=snap_entity.eid,
                        file_data=json.dumps(file_data), data_type=data_type)
                    self.w(u'<div id="gallery-triplanar" class="leftblock">')
                    self.w(u'<iframe  frameborder="0" scrolling="auto" s'
                            'tyle="width:100%; height:1000px" '
                            'src="{0}">'.format(
                                href))
                    self.w(u'</div>')
                    self.w(u'</iframe>')
                # > display the surfaces
                elif snap_entity.viewer == "SURF":
                    self.w(u'<div id="gallery-img">')
                    json_stats = self._cw.vreg.config["json_population_stats"]
                    if not os.path.isfile(json_stats):
                        json_stats = os.path.join(
                            os.path.dirname(zeijemol.__file__), "data",
                            "qcsurf", "population_mean_sd_default.json")
                    self.wview("mesh-qcsurf", None, "null",
                               filepaths=filepaths,
                               header=[snapset_entity.name],
                               populationpath=json_stats)
                    self.w(u'</div>')

            # Clear float
            self.w(u'<div id="floating-clear"/>')
