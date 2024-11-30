.. _virtualenv: https://virtualenv.pypa.io
.. _pip: https://pip.pypa.io
.. _Pytest: http://pytest.org
.. _Napoleon: https://sphinxcontrib-napoleon.readthedocs.org
.. _Flake8: http://flake8.readthedocs.org
.. _Sphinx: http://www.sphinx-doc.org
.. _tox: http://tox.readthedocs.io
.. _livereload: https://livereload.readthedocs.io
.. _twine: https://twine.readthedocs.io

.. _development_intro:

===========
Development
===========

Development requirements
************************

diskette is developed with:

* *Test Development Driven* (TDD) using `Pytest`_;
* Respecting flake and pip8 rules using `Flake8`_;
* `Sphinx`_ for documentation with enabled `Napoleon`_ extension (using
  *Google style*);
* `tox`_ to run tests on various environments;

Every requirements are available in package extra requirements in section
``dev``.

.. _development_install:

Install for development
***********************

First ensure you have `pip`_ and `virtualenv`_ packages installed then
type: ::

    git clone https://github.com/emencia/diskette.git
    cd diskette
    make install

diskette will be installed in editable mode from the
latest commit on master branch with some development tools.

Unittests
---------

Unittests are made to work on `Pytest`_, a shortcut in Makefile is available
to start them on your current development install: ::

    make tests

Tox
---

To ease development against multiple Python versions a tox configuration has
been added. You are strongly encouraged to use it to test your pull requests.

Just execute Tox: ::

    make tox

This will run tests for all configured Tox environments, it may takes some time so you
may use it only before releasing as a final check.

Documentation
-------------

You can easily build the documentation from one Makefile action: ::

    make docs

There is Makefile action ``livedocs`` to serve documentation and automatically
rebuild it when you change documentation files: ::

    make livedocs

Then go on ``http://localhost:8002/`` or your server machine IP with port 8002.

Note that you need to build the documentation at least once before using
``livedocs``.


Repository workflow
-------------------

Branch ``master`` is always in the last version release state. You never develop
directly on it and only merge release once validated and released.

A new development (feature, fix, etc..) always starts from ``development``.

Each release has its own history branch like ``v1.2.3``.

It is important that ``master`` and ``development`` stay correctly aligned.


Resume for a contributor
........................

#. Start working from a new branch started from the last version of branch
   ``development``;
#. Commit and push your work to your branch;
#. Make a pull request for your branch with target on branch ``development``;
#. You are done.


Resume for a maintainer
.......................

#. Validate a pull request from a contributor;
#. Merge validated branch into branch ``development``;
#. Make a new release (version bump, add changelog, etc..) into branch ``development``
   and push it;
#. Merge branch ``development`` into a new branch named after release version prefixed
   with character ``v`` like ``v1.2.3``;
#. Merge branch ``v1.2.3`` into branch ``master``;
#. Tag release commit with new version ``1.2.3``;
#. Push ``master`` with tags;


Examples
........

A contributor would start like this: ::

    git clone REPOSITORY
    git checkout development origin/development
    git checkout -b my_new_feature
    # ..Then implement your feature..
    git commit -a -m "[NEW] Added new feature X"
    git push origin my_new_feature

At this point contributor need to open a pull request for its feature branch.

Finally a project maintainer would pull the new branch and continue for releasing: ::

    # Merge validated new feature branch into development
    git checkout development
    git merge my_new_feature
    # ..Bump version and update Changelog
    git commit -a -m "[NEW] (v1.2.3) Release"
    git push origin development
    # Finally merge new release into master
    git checkout master
    git merge development
    git tag -a 1.2.3 COMMIT-HASH
    git push --tags origin master
    # Create the version branch
    git checkout -b v1.2.3
    git push origin v1.2.3


Where ``1.2.3`` is dummy sample of a new version.


Releasing
---------

Before releasing, you must ensure about quality, use the command below to run every
quality check tasks: ::

    make quality

If quality is correct and after you have correctly push all your commits
you can proceed to release: ::

    make release

This will build the package release and send it to Pypi with `twine`_.
You will have to
`configure your Pypi account <https://twine.readthedocs.io/en/latest/#configuration>`_
on your machine to avoid to input it each time.

Contribution
------------

* Every new feature or changed behavior must pass tests, Flake8 code quality
  and must be documented.
* Every feature or behavior must be compatible for all supported environment.
