#! /usr/bin/env python
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
import sys
import getpass

# Piws import
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
from zeijemol.importer import SnapsImporter


# Ask for instance & login information
instance_name = raw_input("\nEnter the instance name [default: snapview]: ")
if not instance_name:
    instance_name = "snapview"
login = raw_input("Enter the '{0}' login [default: admin]: ".format(
    instance_name))
if not login:
    login = "admin"
password = getpass.getpass("Enter the '{0}' password [default: alpine]: ".format(
    instance_name))
if not password:
    password = "alpine"


# Define the importer
importer = SnapsImporter(instance_name, login, password)

# Add some raters
importer.add_user("u1", "alpine")
importer.add_user("u2", "alpine")

# Describe some waves
CODE_EXPRESSION = "s\d{1}"
WAVE1_NAME = "wave_1"
WAVE1_CATEGORY = "MRI"
WAVE1_EXPRESSION = "./data/*/mri.*"
WAVE1_DESC = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
WAVE2_NAME = "wave_2"
WAVE2_CATEGORY = "dMRI"
WAVE2_EXPRESSION = "./data/*/dmri.*"
WAVE2_EXTRA = ["atefacts", "noise", "mouvment"]
WAVE2_DESC = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
WAVE3_NAME = "wave_3"
WAVE3_CATEGORY = "QAP"
WAVE3_EXPRESSION = "./data/*/*.pdf"
WAVE3_EXTRA = ["atefacts", "noise", "mouvment"]
WAVE3_DESC = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
CODE_EXPRESSION4 = "\d{12}"
WAVE4_NAME = "wave_4"
WAVE4_CATEGORY = "freesurfer"
WAVE4_EXPRESSION = "./data/fs/*/surf/rh.white.ctm"
WAVE4_EXTRA = ["atefacts"]
WAVE4_DESC = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""

# Import new waves
importer.insert(WAVE1_NAME, WAVE1_CATEGORY, WAVE1_EXPRESSION, CODE_EXPRESSION,
                WAVE1_DESC)
importer.insert(WAVE2_NAME, WAVE2_CATEGORY, WAVE2_EXPRESSION, CODE_EXPRESSION,
                WAVE2_DESC, WAVE2_EXTRA)
importer.insert(WAVE3_NAME, WAVE3_CATEGORY, WAVE3_EXPRESSION, CODE_EXPRESSION,
                WAVE3_DESC, WAVE3_EXTRA)
importer.insert(WAVE4_NAME, WAVE4_CATEGORY, WAVE4_EXPRESSION, CODE_EXPRESSION4,
                WAVE4_DESC, WAVE4_EXTRA)

