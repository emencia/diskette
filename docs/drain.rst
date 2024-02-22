Drain study
===========

This document try to plan how it should works to deliver the right behaviors. "Expected"
sections results are not implemented yet.

.. Note::
    It becomes clear we won't able to easily manage multiple applications in
    ``ApplicationConfig``. It must be enforced at validation level and we won't just
    care about this case internally.

Data labels
***********

There is three kinds of label possible.

App label
    The application label as defined from its AppConfig. It is used as a shortcut to
    avoid defining every model. Django auth contrib application label is ``auth``, once
    resolved it will results to the list of all of app models (``User``,
    ``Group``, etc..).

    Diskette does not use it internally to build command, but this kind of label is
    accepted then resolved to fully qualified model labels.

Simple model label
    This is just the model name, like from ``auth`` app there is ``User``, ``Group``,
    etc..

    It is almost never used internally and not usable with dumpdata command.

Fully qualified label
    Also known as FQM label (Fully Qualified Model label).

    This is the label composed from app label and model label like ``auth.User``,
    ``auth.Group``, etc..

    This the kind of label that is used internally in diskette to build dumpdata
    commands.


Apps and their models
*********************

+---------------------+----------------------+------------------+
| django.contrib.auth | django.contrib.sites | djangoapp_sample |
+=====================+======================+==================+
| User                | Site                 | Blog             |
+---------------------+----------------------+------------------+
| Group               |                      | Category         |
+---------------------+----------------------+------------------+
| Permission          |                      | Article          |
+---------------------+----------------------+------------------+
| Session             |                      |                  |
+---------------------+----------------------+------------------+


Configs in order
****************

+-------------------+--------------------------------+----------------------+------------------------------+
|                   | django.contrib.auth            | django.contrib.sites | sample                       |
+===================+================================+======================+==============================+
| Models            | auth                           | Unconfigured         | sample.Blog, sample.Article  |
+-------------------+--------------------------------+----------------------+------------------------------+
| Resolved labels   | auth.User, auth.Group          | Unconfigured         | sample.Blog, sample.Article  |
|                   | auth.Permission, auth.Session  |                      |                              |
+-------------------+--------------------------------+----------------------+------------------------------+
| Excludes          | auth.Permission, auth.Session  | Unconfigured         |                              |
+-------------------+--------------------------------+----------------------+------------------------------+
| Resolved excludes | auth.Permission, auth.Session  | Unconfigured         | sample.Category              |
+-------------------+--------------------------------+----------------------+------------------------------+

.. Hint::
    We should scan fully qualified labels and validate there are from the same app, it
    would be to difficult for now to manage labels from different apps in the
    definition.


Expected drainages
******************

*Assume 'drain_excluded' is enabled*

+----------------+---------------------+----------------------+---------------------+
|                | Not any allow_drain | Allow_drain for auth | Allow_drain for all |
+================+=====================+======================+=====================+
| Drained models | * sites.Site        | * auth.Permission    | * auth.Permission   |
|                |                     | * auth.Session       | * auth.Session      |
|                |                     | * sites.Site         | * sites.Site        |
|                |                     |                      | * sample.Category   |
+----------------+---------------------+----------------------+---------------------+

Expected commands
*****************

Not any allow_drain
    ::

        dumpdata auth.User auth.Group
        dumpdata sample.Blog sample.Article
        # The drain
        dumpdata --exclude auth.User --exclude auth.Group --exclude auth.Permission \
          --exclude auth.Session --exclude sample.Blog --exclude sample.Article \
          --exclude sample.Category

    ``Site`` will be the only one to be drained, all other implied models from apps are
    excluded because they dont enable ``allow_drain``.

Allow_drain for auth
    ::

        dumpdata auth.User auth.Group
        dumpdata sample.Blog sample.Article
        # The drain
        dumpdata --exclude auth.User --exclude auth.Group --exclude sample.Blog \
          --exclude sample.Article --exclude sample.Category

    In addition to ``Site`` the models ``Permission`` and ``Session`` will be drained
    since ``django.contrib.auth`` app allows to drain it remaining models with
    ``allow_drain``.

Allow_drain for all
    ::

        dumpdata auth.User auth.Group
        dumpdata sample.Blog sample.Article
        # The drain
        dumpdata --exclude auth.User --exclude auth.Group --exclude sample.Blog \
          --exclude sample.Article

    All apps allows to drain their remaining models with ``allow_drain`` so ``Site``,
    ``Permission``, ``Session`` and ``Category`` will be drained.

DrainApplicationConfig.drain_excluded
    When disabled, the drain should work almost like with *Not any allow_drain* case,
    since the drain refuses itself to anything from applications.

    When enabled, it just work as every cases demonstrated before.


Conclusion
**********

Resolver
    Application model should include (by the way of resolver inheritance) everything
    to compute the resolved models to dump and the resolved excludes.

Resolved excludes
    This is something to implement yet in application resolver and model. It will not
    participate to compute the model labels to include in command, its usage will be
    reserved to Drain computation.

    This would require to open apps and search for all existing model and delta with
    resolved labels to get the remaining ones that are implicitely excluded then append
    it to the explicitely excluded from "--excludes".

Fully qualified label in excludes
    ``sample`` from table *Configs in order* defines only a set of models with FQM
    labels, without any excludes items.

    Currently the resolver won't be able to resolve all involved models and
    will ignore that there are app models that are implicitely excluded (since not
    expliciterly defined).

Implicit and explicit exclusions
    The way we resolve labels and use them will create two kinds of exclusion:

    * Explicitely excluded labels given as ``excludes`` argument to application model;
    * Implicitely excluded labels computed from missing app labels from resolved models;

    Finally, they should serve the same purpose when used from drain that should merge
    them to know exclusion.

Drain technically
    Basically the drain will:

    * Excludes application FQM labels, because it must not dump data already
      dumped from applications;
    * Also excludes excluded app models (both implicit and explicit), because on
      default the app excludes are unwanted datas;

    When an app enables ``allow_drain`` it means for drain that it continues to excludes
    application inclusions but is allowed to dump application exclusions and so it won't
    defines them as excludes in its command.

    When drain enables ``drain_excluded`` it means it don't want to dump app exclusions,
    no matter they allow him to do so or not. In this case the drain only perform the
    basic behavior to only dump data from undefined applications (like ``sites.Site``
    in our samples).

Why options to allow drainage or not at different level?
    Because application may have model for temporary data, private data or relation
    index (like M2M) that is really unwanted to dump, so application should be the
    first one to define if remaining model could be dumped in drainage or not.

    Combined to some other case, the options becomes useful so users can use shared
    application definitions and still dediced finally theirselves if drainage is
    desired or not on some projects.

Application dumpdata command
    Application dumpdata command will define explicitely the models to dump with FQM
    labels (either they are defined as fully qualified or app labels) and so
    won't need to define any excludes.

Drain dumpdata command
    As it can be seen in *Expected commands* the drain command will work in an almost
    opposed way than Application: it does not explicitely define any label for
    inclusion so it will drain everything that won't be explicitely excluded.

    Exclusion item will be computed drastically from resolver depending application
    option ``allow_drain`` and drain option ``drain_excluded`` to ensure the drain
    respect application rules.
