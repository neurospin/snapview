##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import division
import os
import json
import time
from StringIO import StringIO
import csv

# CW import
from cubicweb.view import View
from cubicweb.predicates import match_user_groups
from cubicweb.predicates import authenticated_user


class Status(View):
    """ Custom view to display rate status.

    Depending on your rights you will see your own rate status or a bunch
    of people rates.
    """
    __regid__ = "status-view"
    title = "Status"
    __select__ = authenticated_user()

    def call(self, **kwargs):
        """ Create the status table.
        """
        # Get all the rated snaps ordered by wave name and by raters
        self.w(u"<div class='zeijemol-status'>")
        rset = self._cw.execute(
            "Any WN, SC, UN Where W is Wave, W name WN, W snapsets S, "
            "S scores R, R score SC, R scored_by U, "
            "U login UN")
        if rset.rowcount == 0:
            self.w(u"<h1>No score in the database yet.</h1>")
        snapsets_struct = {}
        for wave_name, score, rater in rset:
            snapsets_struct.setdefault(wave_name, {}).setdefault(
                rater, []).append(score)

        # Get the waves possible scores, ie. table headers
        rset = self._cw.execute(
            "Any WN, SC Where W is Wave, W name WN, W score_definitions SC")
        waves_struct = {}
        for wave_name, score_definition in rset:
            waves_struct[wave_name] = json.loads(score_definition)

        # Construct all table: one for each wave
        for index, wave_name in enumerate(snapsets_struct):

            # Get wave data and labels
            labels = ["UID", "Number of rates"] + waves_struct[
                wave_name]
            records = []
            wave_struct = snapsets_struct[wave_name]

            # Get the number of snaps associated to the current wave
            rset = self._cw.execute("Any COUNT(S) Where W is Wave, W name "
                                    "'{0}', W snapsets S".format(wave_name))
            nb_of_snapsets = rset[0][0]

            # Fill the record
            for rater, scores in wave_struct.items():
                nb_rates = len(scores)
                rater_record = [
                    rater,
                    "{0}/{1}".format(nb_rates, nb_of_snapsets)]
                for score_definition in waves_struct[wave_name]:
                    number_score_definitions = scores.count(score_definition)
                    rater_record.append("{0}/{1}".format(
                        number_score_definitions, nb_rates))
                records.append(rater_record)

            # Call JTableView for html generation of the table
            self.wview("jtable-clientside", None, "null", labels=labels,
                       records=records, csv_export=True, index=index,
                       elts_to_sort=["UID"],
                       title="{0} status".format(wave_name))
        self.w(u"</div>")


class Ratings(View):
    """ Custom view to display rate status per subject.

    This view is usefull for managers that have access to all of the people
    rates.
    """
    __regid__ = "ratings-view"
    title = "Admin status"
    __select__ = authenticated_user() & match_user_groups("managers")

    def call(self, **kwargs):
        """ Create the rates table.
        """
        # Get all the rated snaps ordered by wave name and by raters
        self.w(u"<div class='zeijemol-status'>")
        rset = self._cw.execute(
            "Any WN, SN, D, SC, ESC, UN Where W is Wave, W name WN, "
            "W snapsets S, S name SN, S scores R, R creation_date D, "
            "R score SC, R extra_scores ESC, R scored_by U, U login UN")
        if rset.rowcount == 0:
            self.w(u"<h1>No score in the database yet.</h1>")
            return
        snapsets_struct = {}
        for wave_name, sid, timestamp, score, extra_score, rater in rset:
            snapsets_struct.setdefault(wave_name, {}).setdefault(
                rater, []).append((timestamp, score, extra_score, sid))

        # Get the waves possible scores, ie. table headers
        rset = self._cw.execute(
            "Any WN, SC Where W is Wave, W name WN, W score_definitions SC")
        waves_struct = {}
        for wave_name, score_definition in rset:
            waves_struct[wave_name] = json.loads(score_definition)

        # Construct all table
        labels = ["UID", "TIMESTAMP", "WAVE NAME", "SID", "ANSWER",
                  "EXTRA ANSWERS"]
        records = []
        for index, wave_name in enumerate(snapsets_struct):

            # Fill the record
            wave_struct = snapsets_struct[wave_name]
            for rater, scores_struct in wave_struct.items():
                for timestamp, answers, extra_answers, sid in scores_struct:
                    extra_answers = json.loads(extra_answers)
                    if not isinstance(extra_answers, list):
                        extra_answers = [extra_answers]
                    extra_answers = ",".join(extra_answers)
                    records.append([rater, timestamp.isoformat(), wave_name,
                                    sid, answers, extra_answers])

        # Call JTableView for html generation of the table
        self.wview("jtable-clientside", None, "null", labels=labels,
                   records=records, csv_export=True, index=index,
                   elts_to_sort=["UID"],
                   title="Ratings".format(wave_name))
        self.w(u"</div>")


class JTableView(View):
    """ Create a table view with DataTables.
    """
    __regid__ = "jtable-clientside"
    title = "Table"
    paginable = False
    div_id = "jtable-clientside"
    __select__ = authenticated_user()

    def call(self, labels, records, title, csv_export=True,
             elts_to_sort=None, index=0,
             data_table_url="https://cdn.datatables.net/1.10.10",
             jquery_js="http://code.jquery.com/jquery-1.11.3.min.js",
             jquery_url="https://code.jquery.com/ui/1.11.3",
             fixedcolumns_url="https://cdn.datatables.net/fixedcolumns/3.2.0",
             filteringdelay_url="https://cdn.datatables.net/plug-ins/1.10.10"):
        """ Method that will create a table with client-side processing only.
         It is useful for huge datasets (million of entries).

        An Ajax call is emulated within the JavaScript so this function is
        client side only.

        Parameters
        ----------
        labels: list of string
            the columns labels.
        records: list of list
            the table data.
        title: string
            the title of the table.
        csv_export: bool (optional)
            if True an export button will be available.
        elts_to_sort: list (optional, default [])
            labels of the columns to be sorted
        index: int (optional, default 0)
            increment this parameter to insert multiple tables in the same
            page.
        """
        # Set default element to sort
        if elts_to_sort is None:
            elts_to_sort = []

        # Add css resources
        self._cw.add_css(
            os.path.join(data_table_url, "css/jquery.dataTables.min.css"),
            localfile=False)
        self._cw.add_css(
            os.path.join(fixedcolumns_url,
                         "css/fixedColumns.dataTables.min.css"),
            localfile=False)
        self._cw.add_css(
            os.path.join(jquery_url, "themes/smoothness/jquery-ui.css"),
            localfile=False)

        # Add js resources
        self._cw.add_js(
            jquery_js, localfile=False)
        self._cw.add_js(
            os.path.join(data_table_url, "js/jquery.dataTables.min.js"),
            localfile=False)
        self._cw.add_js(
            os.path.join(fixedcolumns_url,
                         "js/dataTables.fixedColumns.min.js"),
            localfile=False)
        self._cw.add_js(
            os.path.join(filteringdelay_url, "api/fnSetFilteringDelay.js"),
            localfile=False)
        self._cw.add_js(
            os.path.join(jquery_url, "jquery-ui.js"),
            localfile=False)

        # Generate the script
        # > table column headers and sort option
        hide_sort_indices = []
        headers = []
        for cnt, label_text in enumerate(labels):
            # >> select if we can sort this column
            if label_text not in elts_to_sort:
                hide_sort_indices.append(cnt)
            # >> add this column to the table definition parameters
            headers.append({"sTitle": label_text})

        # > begin the script
        html = "<script type='text/javascript'> "
        html += "$(document).ready(function() {"

        # > dumps the answers rset into javascript
        html += "var all_data = {0};".format(json.dumps(records))
        html += "var nbrecordstotal = {0};".format(len(records))
        # > create a cache for search patterns filtering
        html += "var filtered_indices = ['', undefined];"
        # > set the default sorting direction
        html += "var sort_dir = 'asc';"

        # > create the table
        html += "var table = $('#the_table_{0}').dataTable( {{ ".format(index)
        html += "serverSide: true,"

        # > set the ajax callback to fill dynamically the table
        html += "ajax: function ( data, callback, settings ) {"
        # > get the table sorting direction
        html += "var current_sort_dir = data.order[0].dir.toLowerCase();"
        html += "if ( current_sort_dir != sort_dir) {"
        html += "all_data = all_data.reverse();"
        html += "sort_dir = current_sort_dir;"
        html += "}"
        # > create the records array for the page beeing displayed
        html += "var out = [];"
        # > get the ID search field
        html += "var search_pattern = data.search.value.toLowerCase().trim();"
        html += "var nbrecordsfiltered = nbrecordstotal;"
        # > if the search field is not empty
        html += "if (search_pattern != '') {"
        # check the filtered indicies cache
        html += "if (filtered_indices[0] != search_pattern) {"
        html += "filtered_indices[0] = search_pattern;"
        html += "filtered_indices[1] = [];"
        # fill the filtered indicies cache
        html += "for ( var i=0; i<nbrecordstotal ; i++ ) {"
        html += ("if (all_data[i][0].toLowerCase()"
                 ".indexOf(search_pattern) >= 0) {")
        html += "filtered_indices[1].push(i);"
        # close the 'if some occurence of the search pattern is found' loop
        html += "}"
        # close the for loop
        html += "}"
        # > close the filtered indices cache verification
        html += "}"
        html += "nbrecordsfiltered = filtered_indices[1].length;"
        # fill the records array based on the filtered indicies
        html += ("for (var i=data.start, ien=Math.min(data.start+data.length, "
                 "nbrecordsfiltered) ; i<ien ; i++) {")
        html += "out.push( all_data[ filtered_indices[1][i] ] );"
        html += "}"
        # > close the 'if the search field is not empty' condition
        html += "}"
        # > if the search field is empty
        html += "else {"
        # fill the records array without filtering
        html += ("for ( var i=data.start, ien=Math.min(data.start+data.length,"
                 " nbrecordstotal) ; i<ien ; i++ ) {")
        html += "out.push( all_data[i] );"
        # > close the for loop
        html += "}"
        # > close the 'else if the search field is empty' condition
        html += "}"
        # register the ajax callback
        html += "setTimeout( function () {"
        html += "callback( {"
        html += "draw: data.draw,"
        html += "data: out,"
        html += "recordsTotal: nbrecordstotal,"
        html += "recordsFiltered: nbrecordsfiltered"
        html += "} );"
        # > close the ajax callback registration
        html += "}, 50 );"
        # > close the ajax callback
        html += "},"

        # > set table display options
        html += "'scrollCollapse': true,"
        html += "'sPaginationType': 'bootstrap',"
        html += "'processing': true,"
        html += "'scrollY': '600px',"
        if csv_export:
            html += "'dom': 'T<\"clear\">l<\"toolbar\">frtip',"
        else:
            html += "'dom': 'T<\"clear\">lfrtip',"
        html += "'oLanguage': {{'sSearch': '{0} search'}},".format(labels[0])
        html += "'pagingType': 'full_numbers',"

        # > set table header
        html += "'aoColumns': {0},".format(json.dumps(headers))

        # > set sort widget on column
        html += "'aoColumnDefs': [ "
        html += "{{ 'bSortable': false, 'aTargets': {0} }}".format(
            str(hide_sort_indices))
        html += "],"

        # > close table
        html += "} );"

        # > the first column is static in the display
        html += "var fc = new $.fn.dataTable.FixedColumns( "
        html += "table, {leftColumns: 1} "
        html += ");"
        html += "table.fnSetFilteringDelay(1000);"

        if csv_export:

            # > create a new csv download button
            csv_button_html = (u'<p><a class="btn btn-default" role="button" '
                               u'id="csv_button">CSV Export &#187;</a></p>')
            html += u"$('div.toolbar').html('{0}');".format(csv_button_html)

            # > center the search-bar
            html += ("$('#the_table_filter').css({'float': 'none', "
                     "'text-align': 'center'});")

            # > set csv file name
            timestamp = time.strftime("%Y-%m-%d_%H:%M:%S")
            filename = "_".join([title, timestamp])

            # > assign ajax callback to csv button : start function click
            html += "$('#csv_button').click(function() {"

            # > create in-memory csv file using python csv module
            f = StringIO()
            writer = csv.writer(f, delimiter=';')
            # write the headers
            writer.writerow(labels)
            # write all the rows
            writer.writerows(records)
            # get the csv result as string
            result = f.getvalue()

            # > csv file javascript insertion with html compatibility
            # (line break character)
            html += "var result = '{0}';".format(
                    result.replace("\r\n", "\\r\\n"))
            # > create a web-browser download object
            html += "var a = window.document.createElement('a');"
            html += ("a.href = window.URL.createObjectURL(new Blob([result], "
                     "{type: 'text/csv'}));")
            html += "a.download = '{0}.csv';".format(filename)
            html += "document.body.appendChild(a);"
            html += "a.click();"
            html += "document.body.removeChild(a);"

            # > end fct click
            html += "});"

        # > close document section
        html += "} );"

        # Close script div
        html += "</script>"

        # > set a title
        html += "<h1>{0}</h1>".format(title)

        # > display the table in the body
        html += "<table id='the_table_{0}' class='cell-border display'>".format(index)
        html += "<thead></thead>"
        html += "<tbody></tbody>"
        html += "</table>"

        # Creat the corrsponding html page
        self.w(unicode(html))
