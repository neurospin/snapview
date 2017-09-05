##########################################################################
# NSAp - Copyright (C) CEA, 2017
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import json

# CW import
from cubicweb.server import hook

# Jinja2 import
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

# Package import
import cubes.zeijemol as zeijemol
from cubes.zeijemol.migration.update_sources import _create_or_update_ldap_data_source


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


class UpdateSource(hook.Hook):
    """ On startup update the LDAP source if specified.
    """
    __regid__ = "zeijemol.update-source"
    events = ("server_startup", )

    def __call__(self):
        config_file = os.path.join(
            os.path.dirname(zeijemol.__file__), "ldap.config")
        if os.path.isfile(config_file):
            with open(config_file) as configuration_file:
                configuration = json.load(configuration_file)
            with self.repo.internal_cnx() as cnx:
                _create_or_update_ldap_data_source(
                    cnx, configuration, update=True)
