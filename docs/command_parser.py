import argparse
import os
import sys
from pathlib import Path

# Use the documentation settings
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sandbox.settings.documentation")

# Setup Django
import django
django.setup()

from django.utils.module_loading import import_string

from tabulate import tabulate


class DocumentationCommandParser:
    """
    Dummy argument parser to recolt them.
    """
    def __init__(self):
        self.arguments = []

    def add_argument(self, *args, **kwargs):
        """
        Simulate Django ``BaseCommand.add_argument`` to receive argument options and
        compute them to a dictionnary. Option contents will contain some RST syntax.
        """
        type_display = "str"
        if kwargs.get("type"):
            type_display = kwargs.get("type").__name__
        else:
            if kwargs.get("action", "") in ("store_true", "store_false"):
                type_display = "bool"

        argnames = ["``{}``".format(k) for k in args]

        self.arguments.append({
            "names": " / ".join(argnames),
            "type": type_display,
            "metavar": kwargs.get("metavar"),
            "default": str(kwargs.get("default", "")),
            "help": kwargs.get("help"),
        })


class NeutralizedCommand:
    """
    Dummy Command class to inherit after BaseCommand class so it neutralizes it and
    we can just recolt argument options with internal parser to build a documentation
    of command arguments.
    """
    def __init__(self, module_path):
        self.parser = DocumentationCommandParser()

    def get_arguments_documentation(self):
        """
        Build a ReStructuredText table from command arguments.
        """
        self.add_arguments(self.parser)

        import json
        #print(
            #json.dumps(self.parser.arguments, indent=4)
        #)

        args_docs = [
            [arg_doc["names"], arg_doc["type"], arg_doc["help"]]
            for arg_doc in self.parser.arguments
        ]
        #print(
            #json.dumps(args_docs, indent=4)
        #)

        # print(super().__doc__)

        table = tabulate(
            args_docs,
            tablefmt="grid",
            headers=["Option", "Type", "Help"],
        )
        return str(table)


def make_command_documentation(module_path, destination_path):
    print("- Parsing command:", module_path)
    Command = import_string(
        "{}.Command".format(module_path)
    )

    PatchedCommand = type("PatchedCommand", (NeutralizedCommand, Command), {})

    cmd = PatchedCommand(module_path)
    doc = cmd.get_arguments_documentation()

    destination_path.write_text(doc)
    print("  └── Command documentation has been written to:", destination_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Create ReStructuredText table of a Django management command arguments"
        ),
    )
    parser.add_argument(
        "source",
        default=None,
        metavar="MODULEPATH",
        help=(
            "Python path to command (ex: myproject.myapp.management.commands.ping"
        ),
    )
    parser.add_argument(
        "destination",
        type=Path,
        default=None,
        metavar="FILEPATH",
        help=(
            "Filepath where to write content. Existing file will be overwritten."
        )
    )

    args = parser.parse_args()

    make_command_documentation(args.source, args.destination)
