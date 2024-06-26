import json
from pathlib import Path

from django.core.management.base import BaseCommand

from ...core.applications.store import get_appstore
from ...utils.loggers import DjangoCommandOutput


class Command(BaseCommand):
    """
    Diskette definitions discovering.
    """
    help = (
        "Collect enabled applications to build data dump definition samples that "
        "can be used to build application Diskette definitions. Application "
        "order is respecting order of enabled applications from "
        "'settings.INSTALLED_APPS'."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--destination",
            type=Path,
            metavar="PATH",
            default=None,
            help=(
                "File path where to write built definitions. If not given the "
                "definition list is printed to the standard output."
            ),
        )
        parser.add_argument(
            "--app",
            type=str,
            metavar="APPNAME",
            action="append",
            dest="inclusions",
            default=[],
            help=(
                "This is a cumulative argument. If not empty, the definition list "
                "will be filtered with the given app lists. All other apps from "
                "'settings.INSTALLED_APPS' will be ignored. Given app names are not "
                "validated, if invalid will just be ignored."
            )
        )
        parser.add_argument(
            "--exclude",
            type=str,
            metavar="APPNAME",
            action="append",
            dest="exclusions",
            default=[],
            help=(
                "This is a cumulative argument. Given app names will be ignored from "
                "list definition. This have priority over app name inclusions "
                "from the '--app' option."
            )
        )
        parser.add_argument(
            "--format",
            default="python",
            choices=["json", "python"],
            help=(
                "Specifies the output serialization format for definition list. It is "
                "either 'json' or 'python'. Default is 'python'"
            ),
        )

    def handle(self, *args, **options):
        self.logger = DjangoCommandOutput(command=self, verbosity=options["verbosity"])

        definitions = []

        exclusions = options["exclusions"]
        inclusions = [
            name
            for name in options["inclusions"]
            if name not in exclusions
        ]

        appstore = get_appstore()
        registry = appstore.as_dict()

        for appdata in registry:
            if (
                (inclusions and appdata["label"] not in inclusions) or
                appdata["label"] in exclusions
            ):
                continue

            # Default options
            appopts = {
                "comments": appdata["verbose_name"],
                "natural_foreign": True,
                "models": [],
            }

            # We explicitely declare all models instead of short app label, so user
            # can see every models and know what to exclude if needed
            for label in appdata.get("models", []):
                # NOTE: This could be helpful for some times to watch if there are
                # unsupported cases.
                if len(label["label"].split(".")) > 2:
                    raise NotImplementedError((
                        "Model label '{}' has more than two parts, this is currently"
                        "not supported."
                    ).format(label["label"]))

                appopts["models"].append(label["label"])

            # Append app options
            definitions.append([appdata["pythonpath"], appopts])

        # Always serialize to JSON first as a base
        payload = json.dumps(definitions, indent=4)
        if options["format"] == "python":
            payload = payload.replace("true", "True").replace("false", "False")
            payload = payload.replace("null", "None")

        if not options["destination"]:
            self.stdout.write(payload)
        else:
            options["destination"].write_text(payload)
            self.stdout.write(
                "Definitions have been written into: {}".format(options["destination"])
            )
