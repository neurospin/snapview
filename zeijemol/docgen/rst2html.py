##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import re

# Docutils import
from docutils.core import publish_parts


def rst2html(rststr):
    """ Create a html documentation from a rst formated string.

    Parameters
    ----------
    rststr: str (mandatory)
        the rst formated string.

    Returns
    -------
    doc: str
        the corresponding html documentation.
    """
    return publish_parts(rststr, writer_name="html")["html_body"]
