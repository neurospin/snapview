##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
from __future__ import print_function
import os
import glob
import sys
import hashlib
import json
import re

# Cubicweb import
from cubicweb import cwconfig
from cubicweb.dbapi import in_memory_repo_cnx
from cubicweb import Binary
from cubicweb.server.utils import crypt_password

# SnapView import
from zeijemol.docgen.rst2html import rst2html


class WaveImporter(object):
    """ This class enables us to add/update new wave in a CW instance.
    """
    def __init__(self, instance_name, login, password):
        """ Initialize the WaveImporter class.

        Parameters
        ----------
        instance_name: str (mandatory)
            the name of the cubicweb instance based in the 'snapview' cube.
        login: str (mandatory)
            a login.
        password: str (mandatory)
            the corresponding password.
        """
        # Create a cw session
        config = cwconfig.instance_configuration(instance_name)
        self.repo, self.cnx = in_memory_repo_cnx(
            config, login=login, password=password)
        self.session = self.repo._get_session(self.cnx.sessionid)

    ###########################################################################
    #   Public Methods
    ###########################################################################

    def insert(self, wave_name, wave_category, wave_data, wave_description,
               wave_score_definitions, wave_extra_answers=None, verbose=1):
        """ Insert a new wave of snaps.

        Parameters
        ----------
        wave_name: str (mandatory)
            the name of the current wave.
        wave_category: str (mandatory)
            a category used to filter waves.
        wave_data: dict (mandatory)
            a dictionary structure of the form:
            {<subject_id>: {<snap_names>: {filepaths: <filepaths_struct>,
                                           viewer: <viewer_name>}}
            where <filepaths_struct> is a list of paths ('[<paths>]') or a list
            of 2-uplets containing a description and a list of paths
            ('[(<description>, [<paths>])]'). Note that the <filepaths_struct>
            element order is important and saved in the database.
        wave_description: dict (mandatory)
            a dictionnay with a mandatory 'description' key containing the
            description of the wave formated in RST and an optional key
            'filepath' containing a pdf documentation file path.
        wave_score_definitions: list of str (mandatory)
            a list of score definitions.
        wave_extra_answers: list of str (optional, default=None)
            a list of closed possible extra answers.
        verbose: int (optional, default 1)
            control the verbosity level.
        """
        # Format the 'wave_extra_answers' parameter if necessary
        wave_extra_answers = wave_extra_answers or []

        # Transform the RST documentation in HTML
        description = rst2html(wave_description["description"])

        # Insert the wave entity if necessary
        if verbose > 0:
            print("Inserting wave '{0}'...".format(wave_name))
        # > link documentation file
        fpath = wave_description.get("filepath", None)
        # > create wave
        wave_struct = {
            "identifier": self._md5_sum(wave_name),
            "name": wave_name.replace("_", " "),
            "category": wave_category.replace("_", " "),
            "description": description,
            "score_definitions": json.dumps(wave_score_definitions),
            "extra_answers": json.dumps(wave_extra_answers)
        }

        if fpath is not None:
            ext = fpath.split(".")[-1].upper()
            if ext != "PDF":
                raise ValueError("{0}: only PDF documentation files are "
                                 "accepted.".format(wave_name))
            wave_struct["filepath"] = fpath
        wave_entity, wave_created = self._get_or_create_unique_entity(
            rql=("Any X Where X is Wave, X identifier "
                 "'{0}'".format(wave_struct["identifier"])),
            check_unicity=True,
            entity_name="Wave",
            **self._u(wave_struct))
        wave_eid = wave_entity.eid

        # Insert the snaps if necassary
        if verbose > 0:
            print("Inserting '{0}' snapsets...".format(len(wave_data)))
        for snapset_cnt, (sid, snap_data) in enumerate(wave_data.items()):
            # > display progress
            ratio = (snapset_cnt + 1.) / float(len(wave_data))
            self._progress_bar(ratio, title="SNAPSET", bar_length=40)
            # > create snapset entity
            snapset_struct = {
                "identifier": self._md5_sum("{0}_{1}".format(wave_name, sid)),
                "name": sid
            }
            snapset_entity, snapset_created = (
                self._get_or_create_unique_entity(
                    rql=("Any X Where X is SnapSet, X identifier "
                         "'{0}'".format(snapset_struct["identifier"])),
                    check_unicity=True,
                    entity_name="SnapSet",
                    **self._u(snapset_struct)))
            snapset_eid = snapset_entity.eid
            # > insert associated snaps if not already created and add
            # relations
            if snapset_created:
                self._set_unique_relation(
                    snapset_eid, "wave", wave_eid, check_unicity=False)
                self._set_unique_relation(
                    wave_eid, "snapsets", snapset_eid, check_unicity=False)
                self.insert_snaps(snapset_eid, wave_name, sid, snap_data)
            elif verbose > 0:
                print("Snapset '({0}-{1}-{2})' already imported.".format(
                    wave_name, sid, snapset_eid))

        # Commit changes
        self.session.commit()

    def insert_snaps(self, snapset_eid, wave_name, sid, snap_data):
        """ Add 'Snap' viewers to a specific snapset.

        Parameters
        ----------
        snapset_eid: int (mandatory)
            the snapset eid.
        wave_name: str (mandatory)
            the wave name.
        sid: str (mandatory)
            the subject identifier.
        snap_data: dict (mandatory)
            a dictionary structure of the form:
            {<snap_names>: {filepaths: <filepaths_struct>,
                            viewer: <viewer_name>}}
            where <filepaths_struct> is a list of paths ('[<paths>]') or a list
            of 2-uplets containing a description and a list of paths
            ('[(<description>, [<paths>])]'). Note that the <filepaths_struct>
            element order is important and saved in the database.
        """
        for snap_name, snaps in snap_data.items():
            # > create entity
            snap_struct = {
                "identifier": self._md5_sum("{0}_{1}_{2}".format(
                    wave_name, sid, snap_name)),
                "name": snap_name.replace("_", " "),
                "viewer": snaps["viewer"]
            }
            snap_entity, snap_created = self._get_or_create_unique_entity(
                rql=("Any X Where X is Snap, X identifier "
                     "'{0}'".format(snap_struct["identifier"])),
                check_unicity=True,
                entity_name="Snap",
                **self._u(snap_struct))
            snap_eid = snap_entity.eid
            # > insert associated files if not already created and add
            # relations
            if snap_created:
                # >> add relations
                self._set_unique_relation(
                    snap_eid, "snapset", snapset_eid, check_unicity=False)
                self._set_unique_relation(
                    snapset_eid, "snaps", snap_eid, check_unicity=False)
                # >> insert files
                file_cnt = 1
                for file_data in snaps["filepaths"]:
                    if isinstance(file_data, tuple):
                        description, fpaths = file_data
                        for fpath in fpaths:
                            self.insert_file(snap_eid, fpath, file_cnt,
                                            description=description)
                            file_cnt += 1
                    elif isinstance(file_data, basestring):
                        self.insert_file(snap_eid, file_data, file_cnt)
                        file_cnt += 1
                    else:
                        raise ValueError("'{0}' is not a path or a "
                                         "2-uplet.".format(file_data))
        # Commit changes
        self.session.commit()

    def insert_file(self, snap_eid, fpath, order, description=None):
        """ Add 'ExternalFile' to a specific snap.

        Parameters
        ----------
        snap_eid: int (mandatory)
            the snap eid.
        fpath: str (mandatory)
            the file path.
        order: int (mandatory)
            the file order.
        description: str (optional, default None)
            the file description.
        """
        ext = fpath.split(".")[-1].upper()
        with open(fpath, "rb") as open_file:
            sha1hex = self._md5_sum(open_file.read(), algo="sha1")
        file_struct = {
            "identifier": self._md5_sum(fpath),
            "filepath": fpath,
            "order": order,
            "dtype": ext,
            "sha1hex": sha1hex
        }
        if description is not None:
            file_struct["description"] = description
        file_entity, file_created = (
            self._get_or_create_unique_entity(
                rql=("Any X Where X is ExternalFile, X identifier "
                     "'{0}'".format(file_struct["identifier"])),
                check_unicity=True,
                entity_name="ExternalFile",
                **self._u(file_struct)))
        file_eid = file_entity.eid
        self._set_unique_relation(
            file_eid, "snap", snap_eid, check_unicity=False)
        self._set_unique_relation(
            snap_eid, "files", file_eid, check_unicity=False)

    def add_user(self, user_name, password, group_name="users"):
        """ Add a new user in the database.

        Parameters
        ----------
        user_name: str
            the login of the user in the database.
        password: str
            the password of the user in the database.
        group_name: str
            the database group name the user will be rattached to.
        """
        # Get the activated State entity
        rql = "Any X Where X is State, X name 'activated'"
        rset = self.session.execute(rql)
        if rset.rowcount != 1:
            raise Exception("Can't insert users, no activated State entity "
                            "detected.")
        state_eid = rset[0][0]

        # Insert the user
        crypted = crypt_password(password)
        user_entity, is_created = self._get_or_create_unique_entity(
            rql=("Any X Where X is CWUser, X login "
                 "'{0}'".format(user_name)),
            check_unicity=True,
            entity_name="CWUser",
            login=unicode(user_name),
            upassword=Binary(crypted))

        # If the user is created, add relation with the State entity
        if is_created:

            # Activate the account
            self._set_unique_relation(
                user_entity.eid, "in_state", state_eid, check_unicity=False)

            # Add the user to the default group
            rset = self.session.execute(
                "Any X Where X is CWGroup, X name '{0}'".format(group_name))
            if rset.rowcount != 1:
                raise Exception(
                    "Can't insert user '{0}' in group '{1}', got {2} "
                    "matches.".format(user_name, group_name, rset.rowcount))
            group_eid = rset[0][0]
            self._set_unique_relation(
                user_entity.eid, "in_group", group_eid, check_unicity=False)

    ###########################################################################
    #   Private Methods
    ###########################################################################

    def _md5_sum(self, path, algo="md5"):
        """ Create a md5 sum of a path.

        Parameters
        ----------
        path: str (madatory)
            a string to hash.

        Returns
        -------
        out: str
            the input hashed string.
        """
        if hasattr(hashlib, algo):
            m = getattr(hashlib, algo)()
        else:
            m = hashlib.md5()
        m.update(path)
        return m.hexdigest()

    def _progress_bar(self, ratio, title="", bar_length=40, maxsize=20):
        """ Method to generate a progress bar.

        Parameters
        ----------
        ratio: float (mandatory 0<ratio<1)
            float describing the current processing status.
        title: str (optional)
            a title to identify the progress bar.
        bar_length: int (optional)
            the length of the bar that will be ploted.
        maxsize: int (optional)
            use to justify title.
        """
        progress = int(ratio * 100.)
        block = int(round(bar_length * ratio))
        title = title.ljust(maxsize, " ")
        text = "\r[{0}] {1}% {2}".format(
            "=" * block + " " * (bar_length - block), progress, title)
        sys.stdout.write(text)
        sys.stdout.flush()
        if ratio == 1:
            print("")

    def _u(self, struct):
        """ Transform string to unicode

        Parameters
        ----------
        struct: dict
            a simple one level dictionary.
        """
        for key, value in struct.items():
            if isinstance(value, str):
                struct[key] = unicode(value)
        return struct

    ###########################################################################
    #   Private Insertion Methods
    ###########################################################################

    def _set_unique_relation(self, source_eid, relation_name, detination_eid,
                             check_unicity=True, subjtype=None):
        """ Method to create a new unique relation.

        First check that the relation do not exists if 'check_unicity' is True.

        Parameters
        ----------
        source_eid: int (madatory)
            the CW identifier of the object entity in the relation.
        relation_name: str (madatory)
            the relation name.
        detination_eid: int (madatory)
            the CW identifier of the subject entity in the relation.
        check_unicity: bool (optional)
            if True check if the relation already exists in the data base.
        subjtype: str (optional)
            give the subject etype for inlined relation when using a store.
        """
        # With unicity contrain
        if check_unicity:

            # First build the rql request
            rql = "Any X Where X eid '{0}', X {1} Y, Y eid '{2}'".format(
                source_eid, relation_name, detination_eid)

            # Execute the rql request
            rset = self.session.execute(rql)

            # The request returns some data -> do nothing
            if rset.rowcount == 0:
                self.session.add_relation(
                    source_eid, relation_name, detination_eid)

        # Without unicity constrain
        else:
            self.session.add_relation(
                source_eid, relation_name, detination_eid)

    def _get_or_create_unique_entity(self, rql, entity_name,
                                     check_unicity=True, *args, **kwargs):
        """ Method to create a new unique entity.

        First check that the entity do not exists by executing the rql request
        if 'check_unicity' is True.

        Parameters
        ----------
        rql: str (madatory)
            the rql request to check unicity.
        entity_name: str (madatory)
            the name of the entity we want to create.
        check_unicity: bool (optional)
            if True check if the entity already exists in the data base.

        Returns
        -------
        entity: CW entity
            the requested entity.
        is_created: bool
            return True if the entity has been created, False otherwise.
        """
        # Initilize output prameter
        is_created = False

        # With unicity contrain
        if check_unicity:
            # First execute the rql request
            rset = self.session.execute(rql)

            # The request returns some data, get the unique entity
            if rset.rowcount > 0:
                if rset.rowcount > 1:
                    raise Exception("The database is corrupted, please "
                                    "investigate.")
                entity = rset.get_entity(0, 0)
            # Create a new unique entity
            else:
                entity = self.session.create_entity(entity_name, **kwargs)
                is_created = True
        # Without unicity constrain
        else:
            entity = self.session.create_entity(entity_name, **kwargs)
            is_created = True

        return entity, is_created
