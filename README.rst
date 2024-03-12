.. _Python: https://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _django-sendfile2: https://github.com/moggers87/django-sendfile2

========
Diskette
========

Export and import Django application datas and medias.


Features
********

* Based on *Django apps* to know about applications and their models;
* Application datas are dumped with Django ``dumpdata`` command as JSON fixtures, dumps
  can be naturally loaded in any database type using Django command  ``loaddata``;
* Define application to be dumped with multiple options;
* Advanced data drainage for undefined applications;
* Media archiving is done through *Storages* (not *Django storages*) that can be
  whatever directory you need to backup;
* Many excluding rules for datas and storages to avoid useless content in archive;
* Build a complete archive that can be automatically loaded with Diskette or manually;
* Support models made with ``django-polymorphic``;


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
