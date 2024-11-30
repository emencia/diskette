.. _Python: https://www.python.org/
.. _Django: https://www.djangoproject.com/
.. _datalookup: https://datalookup.readthedocs.io/
.. _Requests: https://requests.readthedocs.io/en/latest/
.. _Django Sendfile: https://github.com/moggers87/django-sendfile2
.. _Django Applications: https://docs.djangoproject.com/en/stable/ref/applications/
.. _dumpdata command: https://docs.djangoproject.com/en/stable/ref/django-admin/#dumpdata
.. _loaddata command: https://docs.djangoproject.com/en/stable/ref/django-admin/#loaddata
.. _django-polymorphic: https://github.com/jazzband/django-polymorphic
.. _fixtures: https://docs.djangoproject.com/en/stable/topics/db/fixtures/

========
Diskette
========

Export and import Django application datas and medias.


Features
********

* Based on `Django Applications`_ to know about applications and their models;
* Application datas are dumped with `dumpdata command`_ command as JSON `fixtures`_;
* Dump archive can be naturally loaded in any database type using Django command
  `loaddata command`_;
* You define applications to be dumped (or not) with multiple options;
* Advanced data drainage for undefined applications;
* Media archiving is done through storage paths (not *Django storages*) that can be
  whatever directory you need to backup;
* Many excluding rules for datas and storages to avoid useless content in archive;
* Build a complete archive that can be automatically loaded with Diskette or manually;
* Support models made with `django-polymorphic`_;
* Django admin interface to manage dumps and API keys;
* Diskette load command can get a dump archive either from a local file, a simple
  archive URL to download or automatically from the Django admin view (securized with
  API key);


Dependencies
************

* `Python`_>=3.9;
* `Django`_>=4.0;
* `datalookup`_>=1.0.0;
* `Requests`_>=2.32.3;
* `Django Sendfile`_>=0.7.0;


Links
*****

* Read the documentation on `Read the docs <https://diskette.readthedocs.io/>`_;
* Download its `PyPi package <https://pypi.python.org/pypi/diskette>`_;
* Clone it on its `Github repository <https://github.com/emencia/diskette>`_;


Credits
*******

Logo vector and icon by `SVG Repo <https://www.svgrepo.com>`_.
