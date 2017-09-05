# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2017
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" If a 'ldap.config' file is declared within the module, an automatic sync is
declared using the following functions.
"""

# Set LDAP source
import os
import json
import cubes.zeijemol as zeijemol


_LDAP_CONFIGURATION = u"""
# Is the repository responsible to automatically import content from this
# source? You should say yes unless you don't want this behaviour or if you use
# a multiple repositories setup, in which case you should say yes on one
# repository, no on others.
synchronize=yes
# Interval in seconds between synchronization with the external source (default
# to 5 minutes, must be >= 1 min).
synchronization-interval=%(synchronization-interval)s
# Maximum time allowed for a synchronization to be run. Exceeded that time, the
# synchronization will be considered as having failed and not properly released
# the lock, hence it won't be considered
max-lock-lifetime=30min
# Should already imported entities not found anymore on the external source be
# deleted?
delete-entities=yes
# Time before logs from datafeed imports are deleted.
logs-lifetime=10d
# Timeout of HTTP GET requests, when synchronizing a source.
http-timeout=1min
# authentication mode used to authenticate user to the ldap.
auth-mode=simple
# realm to use when using gssapi/kerberos authentication.
#auth-realm=
# user dn to use to open data connection to the ldap (eg used to respond to rql
# queries). Leave empty for anonymous bind
data-cnx-dn=%(data-cnx-dn)s
# password to use to open data connection to the ldap (eg used to respond to
# rql queries). Leave empty for anonymous bind.
data-cnx-password=%(data-cnx-password)s
# base DN to lookup for users; disable user importation mechanism if unset
user-base-dn=%(user-base-dn)s
# user search scope (valid values: "BASE", "ONELEVEL", "SUBTREE")
user-scope=ONELEVEL
# classes of user (with Active Directory, you want to say "user" here)
user-classes=top,posixAccount
# additional filters to be set in the ldap query to find valid users
user-filter=
# attribute used as login on authentication (with Active Directory, you want to
# use "sAMAccountName" here)
user-login-attr=uid
# name of a group in which ldap users will be by default. You can set multiple
# groups by separating them by a comma.
user-default-group=users
# map from ldap user attributes to cubicweb attributes (with Active Directory,
# you want to use
# sAMAccountName:login,mail:email,givenName:firstname,sn:surname)
user-attrs-map=%(user-attrs-map)s
# base DN to lookup for groups; disable group importation mechanism if unset
group-base-dn=%(group-base-dn)s
# group search scope (valid values: "BASE", "ONELEVEL", "SUBTREE")
group-scope=ONELEVEL
# classes of group
group-classes=top,posixGroup
# additional filters to be set in the ldap query to find valid groups
group-filter=
# map from ldap group attributes to cubicweb attributes
group-attrs-map=%(group-attrs-map)s"""


def _escape_rql(request):
    return request.replace('\\', '\\\\').replace("'", "\\'")


def _create_or_update_ldap_data_source(session, config, update=False):
    """ Create the LDAP data source if not already created. Update the LDAP
    data if requested.
    """
    attributes = {
        u'name': u'Zeijemol-Source',
        u'type': u'ldapfeed',
        u'config': _escape_rql(_LDAP_CONFIGURATION % config),
        u'url': config["url"],
        u'parser': u'ldapfeed',
    }

    name = attributes[u"name"]
    req = "Any X WHERE X is CWSource, X name '%(name)s'" % {"name": name}
    rset = session.execute(req)

    if rset.rowcount == 1 and update:
        session.info("Updating source '%s'..." % name)
        req = "SET"
        for attribute, value in attributes.iteritems():
            req += " X %(attribute)s '%(value)s'," % {"attribute": attribute,
                                                      "value": value}
        req = req[:-1]
        req += " WHERE X is CWSource, X name '%(name)s'" % {"name": name}
    elif rset.rowcount == 0:
        session.info("Creating source '%s'..." % name)
        req = "INSERT CWSource X:"
        for attribute, value in attributes.iteritems():
            req += " X %(attribute)s '%(value)s'," % {"attribute": attribute,
                                                      "value": value}
        req = req[:-1]
    else:
        print("Existing source '%s' (%i)." % (name, rset[0][0]))

    rset = session.execute(req)
    session.commit()


