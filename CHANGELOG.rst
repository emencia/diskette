
=========
Changelog
=========

Version 0.3.0 - Unreleased
--------------------------

* Added ``diskette_load`` command;
* Added ``diskette_apps`` command;
* Added ``polymorphic_dumpdata`` command, a work around for issues with application
  models that use ``django-polymorphic``;
* Lots of refactoring to include an application store to properly resolve and manage
  data dump with application models;
* Many adjustments to make dump and loading work;
* Added contribution modules for ``django-configuration`` and ``project-composer``;


Version 0.2.0 - Not released as a package
-----------------------------------------

* Implemented storages dump chain;
* Added ``diskette_dump`` command;
* Implemented all usefull options;
* Added test coverage for the dump chain;


Version 0.1.0 - Not released as a package
-----------------------------------------

* Started with ``cookiecutter-sveetch-djangoapp==0.7.0``;
* Added dump management with Django ``dumpdata`` command;
