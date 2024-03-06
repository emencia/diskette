class DisketteDefinitionsCollector:
    """
    Diskette definition collector for 'project-composer'.
    """
    def define(self):
        return []

    def get_definitions(self):
        return [d for d in self.define()]
