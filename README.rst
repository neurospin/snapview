===================
Ratings Web Service
===================

Summary
=======

This tool (also denoted as a cube in the CubicWeb jargon) is a helper to
create a rating web service.
Such web service is very usefull when people have to deal with large
cohorts QA/QC (snaps/images/meshes/...).
It is based on the CubicWeb core technology (a semantic web
application framework) and integrates the
'qcsurf' github project functionalitites.
The raters access custom views through HTTP/HTTPS to rate new items
or to visualize the rating process status.

HowTo
=====

First it is mandatory to install cubicweb::

    https://docs.cubicweb.org/book/admin/setup.

Then a 'toy_instance' instance has to be created based on the proposed cube::

    cubicweb-ctl create zeijemol toy_instance
    cubicweb-ctl start -Dlinfo toy_instance (ready on localhost:8080)

It is now possible to add new data in the database for ratings::

    from snapview.importer import SnapsImporter

    importer = SnapsImporter("toy_instance", "my_login", "my_password")
    importer.insert("wave 1", "FreeSurfer", "./data/fs/*/surf/rh.white.ctm",
                    "\d{12}", "Some description")
    ...
    firefox localhost:8080

Utils
=====

A utility function is proposed to convert FreeSurfer mesh. It requires the
'openctm' package::

    from snapview.importer import fsmesh2ctm

    fsmesh2ctm("./data/fs/s1/surf/rh.white", "./data/fs/s1/surf/")
    



