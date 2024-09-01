
=========
Changelog
=========

Version 0.3.6 - Unreleased
--------------------------

* Minor fixes in Makefile, documentation and pytest adopted options
* Implemented loaddata option ``ignorenonexistent``;


Version 0.3.5 - 2024/03/31
--------------------------

* Added option ``--exclude-data`` to ``diskette_load`` to exclude some dump filenames
  from loading;
* Added setting ``DISKETTE_LOAD_MINIMAL_FILESIZE`` to filter out dumps with file size
  under the size limit;


Version 0.3.4 - 2024/03/30
--------------------------

* Added options ``--app`` and  ``--exclude`` to  ``diskette_apps``;
* Removed forgotten debug print from dump code;


Version 0.3.3 - 2024/03/28
--------------------------

* Added option ``--check`` to ``diskette_dump`` to perform validation and checking
  without to query database or writing anything onto filesystem;
* Added option ``--format`` to ``diskette_apps`` with additional ``python`` format
  which is now the default one instead of ``json``;
* Changed ``diskette_dump`` and ``diskette_load`` so they output Diskette version
  as an early debug log message;


Version 0.3.2 - 2024/03/25
--------------------------

* Added support of archive URL to download in ``diskette_load``;
* Added options for archive checksum creation and comparison in ``diskette_load``;
* Added option for archive checksum creation in ``diskette_dump``;
* Improve handlers test coverage on options;


Version 0.3.1 - 2024/03/21
--------------------------

Fix release for missing commandline script from package.


Version 0.3.0 - 2024/03/21
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
