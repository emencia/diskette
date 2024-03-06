from project_composer.processors import ClassProcessor


class DisketteDefinitionsProcessor(ClassProcessor):
    """
    'project-composer' Processor to collect Diskette application definitions from
    enabled applications.
    """
    def get_module_path(self, name):
        """
        Return a Python path for a module name.

        Arguments:
            name (string): Module name.

        Returns:
            string: Module name prefixed with repository path if it is not empty else
            returns just the module name.
        """
        return "{base}.{part}".format(
            base=self.composer.get_application_base_module_path(name),
            part="disk",
        )
