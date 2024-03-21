
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
* Added ``project-composer`` as a documentation requirement;

**Diskette enters in its Beta stage**

Diskette bases are there and should be working well, however it currently still have
some lacks:

* It is currently a commandline tool only, there is no admin interface yet although it
  has been planned;
* Possible errors from validations are not well managed yet, it means they may be
  outputed as raw exceptions instead of human friendly messages;
* Some commandlines lacks of some helpful arguments;
* Documentation is still in progress;
* Some bugs may be present with some options or specific configurations. This is the
  goal of the Beta stage to find them and fix them;


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
