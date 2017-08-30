##########################################################################
# NSAp - Copyright (C) CEA, 2017
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# CW import
from cubicweb.server import hook

# Jinja2 import
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape


class ConfigureTemplateEnvironment(hook.Hook):
    """ On startup create jinja2 template environment.
    """
    __regid__ = "zeijemol.jinja2-template"
    events = ("server_startup", )

    def __call__(self):
        template_env = Environment(
            loader=PackageLoader("cubes.zeijemol", "templates"),
            autoescape=select_autoescape(["html", "xml"]))
        self.repo.vreg.template_env = template_env
