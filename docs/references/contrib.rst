.. _references_contrib_intro:

=======
Contrib
=======

.. _references_contrib_django_configuration:

Django configuration class
**************************

.. automodule:: diskette.contrib.django_configuration
   :members:


Project composer classes
************************

These are some useful classes to use Diskette within a project made with
`Project composer <https://project-composer.readthedocs.io/>`_.

.. automodule:: diskette.contrib.composer.collectors
   :members:

.. automodule:: diskette.contrib.composer.processors
   :members:

Definitions collect sample
--------------------------

As a sample you may consider the following script example that use the previously
described collector and processor to collect Diskette definition from composed
application: ::

    import logging
    import json
    from pathlib import Path

    from diskette.contrib.composer.collectors import DisketteDefinitionsCollector
    from diskette.contrib.composer.processors import DisketteDefinitionsProcessor

    from project_composer.logger import init_logger
    from project_composer.compose import Composer


    if __name__ == "__main__":
        # Only critical error logs are allowed to no pollute debug output
        init_logger("project-composer", logging.ERROR)

        _composer = Composer(Path("./pyproject.toml").resolve(),
            processors=[DisketteDefinitionsProcessor],
        )

        # Resolve dependency order
        _composer.resolve_collection(lazy=False)

        # Get all application Diskette classes
        _classes = _composer.call_processor("DisketteDefinitionsProcessor", "export")

        # Reverse the list since Python class order is from the last to the first
        _classes.reverse()

        # Add the base collector as the base inheritance
        _COMPOSED_CLASSES = _classes + [DisketteDefinitionsCollector]

        # Compose the final classe
        DisketteDefinitions = type("DisketteDefinitions", tuple(_COMPOSED_CLASSES), {})

        # Collect all definitions in the right order
        definitions = DisketteDefinitions()

        destination = Path("./var/diskette.json")
        # And finally output all collected definitions
        destination.write_text(
            json.dumps(definitions.get_definitions(), indent=4)
        )
        print("Diskette definitions have been written to:", destination.resolve())
