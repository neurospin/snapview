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
import glob

# Cubicweb import
from cubicweb.utils import admincnx

# Zeijemol import
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
from zeijemol.importer import WaveImporter


# Ask for instance & login information
instance_name = raw_input("\nEnter the instance name [default: qc]: ")
if not instance_name:
    instance_name = "qc"

# Describe some waves
WAVE1_NAME = "wave_1"
WAVE1_CATEGORY = "T1"
WAVE1_SCOREDEFS = ["Good", "Bad"]
WAVE1_DATA = {
    "001": {
        "conversion_t1": {
            "filepaths": ["./data/001/t1/3DT1.pdf"],
            "viewer": "FILE"
        }
    },
    "002": {
        "conversion_t1": {
            "filepaths": ["./data/002/t1/3DT1.pdf"],
            "viewer": "FILE"
        },
        "conversion_t1_extra": {
            "filepaths": ["./data/002/t1/3DT1.pdf"],
            "viewer": "FILE"
        }
    },
    "003": {
        "conversion_t1": {
            "filepaths": ["./data/003/t1/3DT1.pdf"],
            "viewer": "FILE"
        }
    }
}
WAVE1_DESC = {}
WAVE1_DESC["description"] = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
WAVE2_NAME = "wave_2"
WAVE2_CATEGORY = "dMRI"
WAVE2_SCOREDEFS = ["Good", "Bad"]
WAVE2_DATA = {
    "001": {
        "dmri_b0": {
            "filepaths": ["./data/001/dmri/HARDI_b0.pdf"],
            "viewer": "FILE"
        },
        "dmri_dwi": {
            "filepaths": ["./data/001/dmri/HARDI_dwi.pdf"],
            "viewer": "FILE"
        }
    },
    "002": {
        "dmri_b0": {
            "filepaths": ["./data/002/dmri/HARDI_b0.pdf"],
            "viewer": "FILE"
        }
    },
    "003": {
        "dmri_b0": {
            "filepaths": ["./data/003/dmri/HARDI_b0.pdf"],
            "viewer": "FILE"
        },
        "dmri_dwi": {
            "filepaths": ["./data/003/dmri/HARDI_dwi.pdf"],
            "viewer": "FILE"
        }
    }
}
WAVE2_EXTRA = ["atefacts", "noise", "mouvment"]
WAVE2_DESC = {}
WAVE2_DESC["description"] = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
WAVE3_NAME = "wave_3"
WAVE3_CATEGORY = "FreeSurfer"
WAVE3_SCOREDEFS = ["ACCEPT", "PRESCRIBE MANUAL EDIT", "REJECT"]
TRIPLANAR_PATTERN = "./data/{0}/t1/triplanar/snapshot-wm-{1}-{2}.png"
WAVE3_DATA = {
    "001": {
        "TRIPLANAR-STACK": {
            "filepaths": [
                ("coronal", [TRIPLANAR_PATTERN.format("001", "C", index) for
                             index in range(0, 256, 2)]),
                ("axial", [TRIPLANAR_PATTERN.format("001", "A", index) for
                           index in range(0, 256, 2)]),
                ("sagittal", [TRIPLANAR_PATTERN.format("001", "S", index) for
                              index in range(0, 256, 2)])],
            "viewer": "TRIPLANAR-STACK"
        },
        "surf": {
            "filepaths": [
                ("ctm", [
                    "./data/001/qcfast/lh.white.ctm",
                    "./data/001/qcfast/lh.pial.ctm",
                    "./data/001/qcfast/rh.white.ctm",
                    "./data/001/qcfast/rh.pial.ctm"]),
                ("stats", [
                    "./data/001/freesurfer/stats/lh.aparc.stats",
                    "./data/001/freesurfer/stats/rh.aparc.stats"])
            ],
            "viewer": "SURF"
        }
    },
    "002": {
        "TRIPLANAR-STACK": {
            "filepaths": [
                ("coronal", [TRIPLANAR_PATTERN.format("002", "C", index) for
                             index in range(0, 256, 2)]),
                ("axial", [TRIPLANAR_PATTERN.format("002", "A", index) for
                           index in range(0, 256, 2)]),
                ("sagittal", [TRIPLANAR_PATTERN.format("002", "S", index) for
                              index in range(0, 256, 2)])],
            "viewer": "TRIPLANAR-STACK"
        },
        "surf": {
            "filepaths": [
                ("ctm", [
                    "./data/002/qcfast/lh.white.ctm",
                    "./data/002/qcfast/lh.pial.ctm",
                    "./data/002/qcfast/rh.white.ctm",
                    "./data/002/qcfast/rh.pial.ctm"]),
                ("stats", [
                    "./data/002/freesurfer/stats/lh.aparc.stats",
                    "./data/002/freesurfer/stats/rh.aparc.stats"])
            ],
            "viewer": "SURF"
        }
    },
    "003": {
        "TRIPLANAR-STACK": {
            "filepaths": [
                ("coronal", [TRIPLANAR_PATTERN.format("003", "C", index) for
                             index in range(0, 256, 2)]),
                ("axial", [TRIPLANAR_PATTERN.format("003", "A", index) for
                           index in range(0, 256, 2)]),
                ("sagittal", [TRIPLANAR_PATTERN.format("003", "S", index) for
                              index in range(0, 256, 2)])],
            "viewer": "TRIPLANAR-STACK"
        },
        "surf": {
            "filepaths": [
                ("ctm", [
                    "./data/003/qcfast/lh.white.ctm",
                    "./data/003/qcfast/lh.pial.ctm",
                    "./data/003/qcfast/rh.white.ctm",
                    "./data/003/qcfast/rh.pial.ctm"]),
                ("stats", [
                    "./data/003/freesurfer/stats/lh.aparc.stats",
                    "./data/003/freesurfer/stats/rh.aparc.stats"])
            ],
            "viewer": "SURF"
        }
    }
}
WAVE3_EXTRA = ["artefacts"]
WAVE3_DESC = {}
WAVE3_DESC["description"] = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
WAVE4_NAME = "wave_4"
WAVE4_CATEGORY = "FreeSurfer"
WAVE4_SCOREDEFS = ["ACCEPT", "PRESCRIBE MANUAL EDIT", "REJECT"]
WAVE4_DATA = {
    "001": {
        "t1": {
            "filepaths": ["./data/001/t1/3DT1.pdf"],
            "viewer": "FILE"
        },
        "aseg": {
            "filepaths": ["./data/001/qcfast/coronal/aseg/slice-C-100.png"],
            "viewer": "FILE"
        },
        "surf": {
            "filepaths": ["./data/001/qcfast/coronal/edges/slice-C-100.png"],
            "viewer": "FILE"
        },
        "aparc": {
            "filepaths": ["./data/001/qcfast/coronal/aparc/slice-C-100.png"],
            "viewer": "FILE"
        }
    },
    "002": {
        "t1": {
            "filepaths": ["./data/002/t1/3DT1.pdf"],
            "viewer": "FILE"
        },
        "aseg": {
            "filepaths": ["./data/002/qcfast/coronal/aseg/slice-C-100.png"],
            "viewer": "FILE"
        },
        "surf": {
            "filepaths": ["./data/002/qcfast/coronal/edges/slice-C-100.png"],
            "viewer": "FILE"
        }
    },
    "003": {
        "t1": {
            "filepaths": ["./data/003/t1/3DT1.pdf"],
            "viewer": "FILE"
        },
        "aseg": {
            "filepaths": ["./data/003/qcfast/coronal/aseg/slice-C-100.png"],
            "viewer": "FILE"
        }
    }
}
WAVE4_EXTRA = ["artefacts"]
WAVE4_DESC = {}
WAVE4_DESC["description"] = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
WAVE4_DESC["filepath"] = "./data/doc.pdf"
WAVE5_NAME = "wave_5"
WAVE5_CATEGORY = "FreeSurfer"
WAVE5_SCOREDEFS = ["ACCEPT", "PRESCRIBE MANUAL EDIT", "REJECT"]
TRIPLANAR_PATTERN = "./data/{0}/t1/triplanar/snapshot-wm-{1}-{2}.png"
WAVE5_DATA = {
    "001": {
        "snaps": {
            "filepaths": [
                ("axial", [TRIPLANAR_PATTERN.format("001", "A", index) for
                           index in range(0, 256, 2)])],
            "viewer": "TRIPLANAR-STACK"
        }
    },
    "002": {
        "snaps": {
            "filepaths": [
                ("axial", [TRIPLANAR_PATTERN.format("002", "A", index) for
                           index in range(0, 256, 2)]),
                ("coronal", [TRIPLANAR_PATTERN.format("002", "C", index) for
                             index in range(0, 256, 2)])],
            "viewer": "TRIPLANAR-STACK"
        }
    }
}
WAVE5_EXTRA = ["artefacts"]
WAVE5_DESC = {}
WAVE5_DESC["description"] = """
Some doc about this wave
------------------------

List of elements

* elem1.
* elem 2.
"""
WAVE6_NAME = "wave_6"
WAVE6_CATEGORY = "T1"
WAVE6_SCOREDEFS = ["ACCEPT", "PRESCRIBE MANUAL EDIT", "REJECT"]
WAVE6_DATA = {
    "001": {
        "t1": {
            "filepaths": [
                "./data/001/avg152T1.nii.gz",
                "./data/001/avg152T2.nii.gz"],
            "viewer": "TRIPLANAR-IMAGE"
        }
    },
    "002": {
        "t1": {
            "filepaths": [
                "./data/002/avg152T1.nii.gz"],
            "viewer": "TRIPLANAR-IMAGE"
        }
    }
}
WAVE6_EXTRA = ["artefacts", "motions"]
WAVE6_DESC = {}
WAVE6_DESC["description"] = """
Some doc about this wave.
"""

# Define the importer
with admincnx(instance_name) as session:
    importer = WaveImporter(instance_name, session)

    # Add some raters
    importer.add_user("u1", "alpine")
    importer.add_user("u2", "alpine")

    # Import new waves
    importer.insert(WAVE1_NAME, WAVE1_CATEGORY, WAVE1_DATA, WAVE1_DESC,
                    WAVE1_SCOREDEFS)
    importer.insert(WAVE2_NAME, WAVE2_CATEGORY, WAVE2_DATA, WAVE2_DESC,
                    WAVE2_SCOREDEFS, WAVE2_EXTRA)
    importer.insert(WAVE3_NAME, WAVE3_CATEGORY, WAVE3_DATA, WAVE3_DESC,
                    WAVE3_SCOREDEFS, WAVE3_EXTRA)
    importer.insert(WAVE4_NAME, WAVE4_CATEGORY, WAVE4_DATA, WAVE4_DESC,
                    WAVE4_SCOREDEFS, WAVE4_EXTRA)
    importer.insert(WAVE5_NAME, WAVE5_CATEGORY, WAVE5_DATA, WAVE5_DESC,
                    WAVE5_SCOREDEFS, WAVE5_EXTRA)
    importer.insert(WAVE6_NAME, WAVE6_CATEGORY, WAVE6_DATA, WAVE6_DESC,
                    WAVE6_SCOREDEFS, WAVE6_EXTRA)

