from ..exceptions import DumpManagerError
from ..utils.lists import get_duplicates

from .models import ApplicationModel
from .serializers import DjangoDumpDataSerializer


class DumpManager:
    """
    Dump manager in in charge of storing application model objects and return
    serialized datas to dump them.
    """
    DEFAULT_SERIALIZER = DjangoDumpDataSerializer

    def __init__(self, apps, executable=None, serializer=None):
        self.apps = self.load(apps)
        self.executable = executable
        serializer = serializer or self.DEFAULT_SERIALIZER
        self.serializer = serializer(executable)

    def load(self, apps):
        """
        Load ApplicationModel objects from given Application data.

        Arguments:
            apps (list):

        Returns:
            list:
        """
        objects = []

        # Check for duplicated name
        twices = list(get_duplicates([name for name, options in apps]))
        if twices:
            raise DumpManagerError(
                "There was some duplicate names from applications: {}".format(
                    ", ".join(twices)
                )
            )

        for name, options in apps:
            objects.append(ApplicationModel(name, **options))

        return objects

    def export_as_payload(self, named=False, commented=False):
        """
        Build a payload dictionnary for each application.

        Keyword Arguments:
            name (boolean): To include or not the name into the dict.
            commented (boolean): To include or not the comments into the dict.

        Returns:
            list:
        """
        return [
            app.as_dict(named=named, commented=commented)
            for app in self.apps
        ]

    def export_as_commands(self, destination=None, indent=None):
        """
        Build dumpdata command line for each application.

        Keyword Arguments:
            destination (string or Path):
            indent (integer):

        Returns:
            list:
        """
        return [
            (
                app.name,
                self.serializer.command(app, destination=destination, indent=indent)
            )
            for app in self.apps
        ]

    def export_with_calls(self, destination=None, indent=None):
        """
        Call dumpdata command to dump each application.

        Keyword Arguments:
            destination (string or Path):
            indent (integer):

        Returns:
            list:
        """
        return [
            (
                app.name,
                self.serializer.call(app, destination=destination, indent=indent)
            )
            for app in self.apps
        ]
