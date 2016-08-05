##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

options = (
    ("json_population_stats", {
        "type": "string",
        "default": "",
        "help": "the json file used to configure the population statistics "
                "for freesurfer naat tool rating. A default json will be used "
                "if not provided",
        "group": "zeijemol",
        "level": 1,
    }),
)
