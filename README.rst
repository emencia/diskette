.. _Python: https://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _django-sendfile2: https://github.com/moggers87/django-sendfile2

========
Diskette
========

Export and import Django application datas and storage directories.


Features
********

* Application datas are managed using Django fixtures in JSON, no need to define
  anything else than application label or models names;
* Advanced data drainage for application datas;
* Storage directories are not Django storages and can be whatever you need until it
  exists under the same base path for all storages;
* Many excluding rules for datas and storages to avoid useless content in archive;
* Build a complete archive that can be automatically loaded with Diskette or manually;


Dependancies
************

* `Python`_>=3.9;
* `Django`_>=4.0,<5.0;
* `django-sendfile2`_>=0.7.0;


Links
*****

* Read the documentation on `Read the docs <https://diskette.readthedocs.io/>`_;
* Download its `PyPi package <https://pypi.python.org/pypi/diskette>`_;
* Clone it on its `Github repository <https://github.com/emencia/diskette>`_;
