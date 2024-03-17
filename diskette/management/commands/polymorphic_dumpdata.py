from pathlib import Path
from io import StringIO

from django.core.management.base import BaseCommand
from django.core import serializers
from django.db.models.query import QuerySet
from django.db import DEFAULT_DB_ALIAS

from ...core.applications.store import get_appstore


class Command(BaseCommand):
    """
    A command alike Django's dumpdata but it enforces usage of
    legacy ``django.db.models.query.QuerySet`` over custom model queryset.

    This is needed to dump data for polymorphic models that won't work properly,
    especially when used from ``django.core.management.call_command``.

    Original code comes from a
    `czpython Gist <https://gist.github.com/czpython/b94c346e4b6cac473bff>`_
    found from
    `django-filer issue 887 <https://github.com/django-cms/django-filer/issues/887#issuecomment-231911757>`_.
    This should resolves problem demonstrated in
    `django-polymorphic issue 175 <https://github.com/jazzband/django-polymorphic/issues/175#issuecomment-1607260352>`_.

    However this only support a few set of legacy dumpdata options:

    * label argument (not finished yet);
    * --exclude (not finished yet);
    * --natural-foreign
    * --natural-primary
    * --output

    Every other options are still present but will raise a NotImplementedError when
    used.
    """  # noqa: E501
    help = (
        "Output the contents of the database as a fixture of the given format. This "
        "is an alternative to Django command 'dumpdata' to support models that "
        "implement usage of 'django-polymorphic'. The argument signatures are "
        "identical but not all legacy options are implemented here."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="app_label[.ModelName]",
            nargs="*",
            help=(
                "Restricts dumped data to the specified app_label or "
                "app_label.ModelName."
            ),
        )
        parser.add_argument(
            "--format",
            default="json",
            help=(
                "Specifies the output serialization format for fixtures. Only 'json' "
                "format is implemented."
            ),
        )
        parser.add_argument(
            "--indent",
            type=int,
            help="Specifies the indent level to use when pretty-printing output.",
        )
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="Nominates a specific database to dump fixtures from. "
            'Defaults to the "default" database. NOT IMPLEMENTED.',
        )
        parser.add_argument(
            "-e",
            "--exclude",
            action="append",
            default=[],
            help="An app_label or app_label.ModelName to exclude "
            "(use multiple --exclude to exclude multiple apps/models).",
        )
        parser.add_argument(
            "--natural-foreign",
            action="store_true",
            dest="use_natural_foreign_keys",
            help="Use natural foreign keys if they are available.",
        )
        parser.add_argument(
            "--natural-primary",
            action="store_true",
            dest="use_natural_primary_keys",
            help="Use natural primary keys if they are available.",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="use_base_manager",
            help=(
                "Use Django's base manager to dump all models stored in the database, "
                "including those that would otherwise be filtered or modified by a "
                "custom manager. NOT IMPLEMENTED."
            ),
        )
        parser.add_argument(
            "--pks",
            dest="primary_keys",
            help=(
                "Only dump objects with given primary keys. Accepts a comma-separated "
                "list of keys. This option only works when you specify one model. "
                "NOT IMPLEMENTED."
            ),
        )
        parser.add_argument(
            "-o",
            "--output",
            type=Path,
            help="Specifies file to which the output is written."
        )

    def export_models(self, inclusions, indent=None, use_natural_foreign_keys=False,
                      use_natural_primary_keys=False, output=None):
        """
        Exports serialized model contents as JSON to output.
        """
        def get_objects():
            for model in inclusions:
                # Restore legacy model Queryset instead of custom one from
                # 'django-polyporphic' that may break dumped data.
                model.objects.queryset_class = QuerySet
                for obj in model.objects.iterator():
                    yield obj

        serializers.serialize(
            "json",
            get_objects(),
            indent=indent,
            use_natural_foreign_keys=use_natural_foreign_keys,
            use_natural_primary_keys=use_natural_primary_keys,
            stream=output,
        )

    def handle(self, *args, **options):
        indent = options["indent"]
        excludes = options["exclude"]
        output = options["output"]
        use_natural_foreign_keys = options["use_natural_foreign_keys"]
        use_natural_primary_keys = options["use_natural_primary_keys"]

        if options["use_base_manager"]:
            raise NotImplementedError("Option '--all' is not implemented.")
        if options["format"] != "json":
            raise NotImplementedError("This command only support the 'json' format.")
        if options["primary_keys"]:
            raise NotImplementedError("Option '--pks' is not implemented.")
        if options["traceback"]:
            raise NotImplementedError("Option '--traceback' is not implemented.")
        if options["database"] != DEFAULT_DB_ALIAS:
            raise NotImplementedError("Option '--using' is not implemented.")

        # Use diskette appstore to resolve labels
        appstore = get_appstore()
        exclusions = appstore.get_models_inclusions(excludes)
        inclusions = appstore.get_models_inclusions(
            args,
            excludes=[item.label for item in exclusions]
        )

        if use_natural_foreign_keys:
            # Alike legacy Django dumpdata, we sort models on dependencies when natural
            # foreign key option is enabled
            # 'sort_dependencies' requires a list of tuple '(AppConfig, model object)'
            # so we need to pack model list
            model_list = serializers.sort_dependencies([
                (appstore.get_app(item.app), [item.object])
                for item in inclusions
            ], allow_cycles=True)
        else:
            # This is a list of nodes, we need to turn them to model objects
            model_list = [item.object for item in inclusions]

        out = StringIO()

        self.export_models(
            model_list,
            indent=indent,
            use_natural_foreign_keys=use_natural_foreign_keys,
            use_natural_primary_keys=use_natural_primary_keys,
            output=out,
        )

        # Either write content to file path if given else write it to standard output
        content = out.getvalue()
        if output:
            output.write_text(content)
        else:
            self.stdout.write(content)
        out.close()
