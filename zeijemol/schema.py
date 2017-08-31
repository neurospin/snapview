##########################################################################
# NSAp - Copyright (C) CEA, 2016
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# CubicWeb import
from yams.buildobjs import EntityType
from yams.buildobjs import String
from yams.buildobjs import Boolean
from yams.buildobjs import Int
from yams.buildobjs import SubjectRelation
from cubicweb.schema import ERQLExpression


###############################################################################
# Modification of the schema
###############################################################################

class Wave(EntityType):
    """ An entity used to store QC wave information.

    Attributes
    ----------
    identifier: String (mandatory)
        a unique identifier for the entity.
    name: String (mandatory)
        a short description of the wave.
    category: String (mandatory)
        a category used to filter waves.
    description: String (mandatory)
        a long description of the wave.
    score_definitions: String (mandatory)
        a list of score definitions.
    extra_answers: String
        a list of closed possible extra answers.

    Relations
    ---------
    snapsets: SubjectRelation
        a snapset is connected to one wave.
    """
    identifier = String(
        required=True,
        unique=True,
        maxsize=64,
        description=u"a unique identifier for the entity.")
    name = String(
        required=True,
        fulltextindexed=True,
        maxsize=256,
        description=u"a short description of the wave.")
    category = String(
        required=True,
        indexed=True,
        maxsize=64,
        description=u"a category used to filter waves.")
    description = String(
        required=True,
        description=u"a long description of the wave.")
    score_definitions = String(
        required=True,
        description=u"a list of score defintions.")
    extra_answers = String(
        description=u"a list of closed possible extra answers.")
    filepath = String(
        description=u"a PDF documentation file path.")
    snapsets = SubjectRelation(
        "SnapSet",
        cardinality="*1",
        inlined=False,
        composite="subject")


class SnapSet(EntityType):
    """ An entity used to group, within each wave, all snaps related to one
    subject.

    Attributes
    ----------
    identifier: String (mandatory)
        a unique identifier for the entity.
    name: String (mandatory)
        a short description of the wave.

    Relations
    ---------
    snaps: SubjectRelation
        a SnapSet is connected to one wave.
    scores: SubjectRelation
        a score is connected to one snapset.
    """
    identifier = String(
        required=True,
        unique=True,
        maxsize=64,
        description=u"a unique identifier for the entity.")
    name = String(
        required=True,
        fulltextindexed=True,
        maxsize=256,
        description=u"a name for the snapset.")
    snaps = SubjectRelation(
        "Snap",
        cardinality="*1",
        inlined=False)
    wave = SubjectRelation(
        "Wave",
        cardinality="1*",
        inlined=False)
    scores = SubjectRelation(
        "Score",
        cardinality="*1",
        inlined=False,
        composite="subject")


class Snap(EntityType):
    """ An entity used to define a specific viewer.

    Attributes
    ----------
    identifier: String (mandatory)
        a unique identifier for the entity.
    name: String (mandatory)
        a short description of the file.
    viewer: String (mandatory)
        the viewer type: 'TRIPLANAR-STACK', 'TRIPLANAR-IMAGE', 'SURF' or 'FILE'.

    Relations
    ---------
    snapset: SubjectRelation
        a snap is connected to one snapset.
    files: SubjectRelation
        a snap is connected to files.
    """
    identifier = String(
        required=True,
        unique=True,
        maxsize=64,
        description=u"a unique identifier for the entity.")
    name = String(
        required=True,
        fulltextindexed=True,
        maxsize=256,
        description=u"a short description for the viewer.")
    viewer = String(
        required=True,
        vocabulary=("TRIPLANAR-STACK", "TRIPLANAR-IMAGE", "SURF", "FILE"),
        description=(u"the viewer type: 'TRIPLANAR-STACK', 'TRIPLANAR-IMAGE', "
                      "'SURF' or 'FILE' are supported."))
    snapset = SubjectRelation(
        "SnapSet",
        cardinality="1*",
        inlined=False)
    files = SubjectRelation(
        "ExternalFile",
        cardinality="*+",
        inlined=False,
        composite="subject")


class ExternalFile(EntityType):
    """ An entity used to store the path to a file on the central
    repository.

    Attributes
    ----------
    identifier: String (mandatory)
        a unique identifier for the entity.
    filepath: String (mandatory)
        the snap file path.
    order: Int (mandatory)
        the file order.
    description: String (mandatory)
        a description for the file.
    sha1hex: String (optional)
        the SHA1 sum of the file.
    dtype: String (mandatory)
        the file type: only 'PDF', 'CTM', 'STATS', 'PNG', 'JPG', 'JPEG' or
        'NIIGZ' are supported.

    Relations
    ---------
    snap: SubjectRelation
        a file is connected to one snap.
    """
    identifier = String(
        required=True,
        unique=True,
        maxsize=64,
        description=u"a unique identifier for the entity.")
    filepath = String(
        required=True,
        description=u"the snap file path.")
    order = Int(
        description=u"the file order.")
    description = String(
        maxsize=50,
        description=u"a description for the file.")
    sha1hex = String(
        maxsize=40,
        description=u"the SHA1 sum of the file.")
    dtype = String(
        required=True,
        vocabulary=("CTM", "STATS", "PNG", "JPEG", "JPG", "PDF", "NIIGZ"),
        description=(u"the file type: 'PDF', 'CTM', 'STATS', 'PNG', 'JPG', "
                      "'JPEG' or 'NIIGZ' are supported."))
    snap = SubjectRelation(
        "Snap",
        cardinality="+*",
        inlined=False)


class Score(EntityType):
    """ An entity used to store the rate associated to a snapset.

    Attributes
    ----------
    identifier: String (mandatory)
        a unique identifier for the entity.
    uid: String (mandatory)
        the user that have scored the snap file.
    score: String (mandatory)
        the user score.

    Relations
    ---------
    snapset: SubjectRelation
        a score is connected to one snapset.
    scored_by: SubjectRelation
        a score is realted to one user of the database.
    """
    identifier = String(
        required=True,
        unique=True,
        maxsize=64,
        description=u"a unique identifier for the entity.")
    uid = String(
        required=True,
        fulltextindexed=True,
        maxsize=64,
        description=u"the user that have scored the snap file")
    score = String(
        required=True,
        description=u"the user score.")
    extra_scores = String(
        description=u"the extra user scores.")
    snapset = SubjectRelation(
        "SnapSet",
        cardinality="1*",
        inlined=False)
    scored_by = SubjectRelation(
        "CWUser",
        cardinality="1*",
        inlined=False,
        composite="object")


###############################################################################
# Set permissions
###############################################################################

SCORE_PERMISSIONS = {
    "read": (
        "managers",
        ERQLExpression("X scored_by U")),
    "add": ("managers", "users"),
    "update": ("managers", ),
    "delete": ("managers", ),
}
Score.set_permissions(SCORE_PERMISSIONS)
