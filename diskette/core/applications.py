from pathlib import Path

from django.apps import apps, AppConfig
from django.db import models
from django.utils.text import slugify

from ..exceptions import ApplicationConfigError, AppModelResolverError

from .defaults import DEFAULT_FORMAT, AVAILABLE_FORMATS


class AppModelResolverAbstract:
    """
    Abstract for methods to resolve model labels from applications
    """
    def normalize_model_name(self, model, app=None):
        """
        Return normalized name for a model.

        Arguments:
            model (object): Model name as a string or Model object (or at least
                anything that inherit from ``django.db.models.base.ModelBase``).

        Keyword Arguments:
            app (Application): Application name or instance, it is optional but
                commonly you should always give it as model label without app prefix
                is subject to conflicts.

        Returns:
            string:
        """
        if app and isinstance(app, AppConfig):
            app = app.label

        if isinstance(model, models.base.ModelBase):
            model = model.__name__

        if not app:
            return model

        return "{}.{}".format(app, model)

    def get_app_models(self, app):
        """
        Return model labels (as ``APPNAME.MODELNAME``) for given application.

        Returns:
            list:
        """
        if isinstance(app, str):
            app = apps.get_app_config(app)

        return [
            self.normalize_model_name(model, app=app)
            for model in app.get_models(
                include_auto_created=True,
                include_swapped=True
            )
        ]

    def get_all_models(self):
        """
        Return all model labels from enabled applications.

        Returns:
            list:
        """
        collected = []

        for app in apps.get_app_configs():
            names = self.get_app_models(app)

            if names:
                collected.extend(names)

        return collected

    def get_label_model_names(self, labels):
        """
        Resolve model names for given labels.

        Arguments:
            labels(string or list): Either labels are model labels (as a string for a
                single one or a list for more) or application labels.

                Application label
                    This will be resolved to a list of names for all of its models, so
                    its useful to select all app models.

                Model label
                    This is just used as it without resolution. so its useful to
                    explicitely define some models, the ones that are not defined will
                    be ignored.

                    A Model label must be in the form "APP.MODEL", a single part would
                    be assumed as an Application label.

        Returns:
            list: List of resolved model names from given labels.
        """
        names = []

        labels = [labels] if isinstance(labels, str) else labels

        for label in labels:
            try:
                app_label, model_label = label.split(".")
            except ValueError:
                names.extend(self.get_app_models(label))
            else:
                if not app_label:
                    raise AppModelResolverError((
                        "Label includes a dot without leading application "
                        "name: {}".format(label)
                    ))

                names.append(self.normalize_model_name(model_label, app=app_label))

        return names


class ApplicationConfig(AppModelResolverAbstract):
    """
    Application model to validate and store application details.

    Arguments:
        name (string): Application name, almost anything but it may be slugified for
            internal usages so avoid too much longer text and special characters.
        models (list): List of model labels.

    Keyword Arguments:
        filename (string): The filename to use if application dump is to be written in
            a file. The filename also determine the format used to dump data. If you
            want another format that the default one you will have to define
            it from the filename even you don't plan to write dump to a file.
            Finally if not given, the filename will be automatically defined with
            slugified ``name`` with default format.
        excludes (list): The list of excluded models that won't be collected into the
            application dump.
        natural_foreign (boolean): Enable usage of natural foreign key.
        natural_primary (boolean): Enable usage of natural primary key.
        comments (string): Free text not used internally.
        allow_drain (boolean): Define if application allows its excluded models to be
            drained. Default is ``False`` to avoid implicit draining of data that may
            not be wanted.

    Attributes:
        is_drain (boolean): Declare application as a special drain application. This
            should always be ``False`` for a common application, ``True`` value is
            reserved to ``DrainApplicationConfig``.
    """
    CONFIG_ATTRS = [
        "name", "models", "excludes", "natural_foreign", "natural_primary", "comments",
        "filename", "is_drain", "allow_drain",
    ]
    OPTIONS_ATTRS = [
        "models", "excludes", "natural_foreign", "natural_primary", "filename",
    ]

    def __init__(self, name, models=[], excludes=None, natural_foreign=False,
                 natural_primary=False, comments=None, filename=None,
                 allow_drain=False):
        self.name = name
        self.models = [models] if isinstance(models, str) else models
        self.excludes = excludes or []
        self.natural_foreign = natural_foreign
        self.natural_primary = natural_primary
        self.comments = comments
        self.filename = filename or self.get_filename()
        self.allow_drain = allow_drain
        self.is_drain = False

    def __repr__(self):
        return "<{klass}: {name}>".format(
            klass=self.__class__.__name__,
            name=self.name
        )

    def get_filename(self, format_extension=None):
        """
        Automatically determine filename from Application name and with a format
        extension name.

        Keyword Arguments:
            format_extension (string):

        Returns
            string:
        """
        return slugify(self.name) + "." + (format_extension or DEFAULT_FORMAT)

    def as_config(self):
        """
        Returns Application configuration suitable for dump history.

        Keyword Arguments:
            name (boolean): To include or not the name into the dict.
            commented (boolean): To include or not the comments into the dict.

        Returns
            dict: Application data.
        """
        return {
            name: getattr(self, name)
            for name in self.CONFIG_ATTRS
        }

    def as_options(self):
        """
        Returns Application options suitable to pass to dumpdata command.

        Keyword Arguments:
            name (boolean): To include or not the name into the dict.
            commented (boolean): To include or not the comments into the dict.

        Returns
            dict: Application data.
        """
        return {
            name: getattr(self, name)
            for name in self.OPTIONS_ATTRS
        }

    def validate(self):
        """
        Validate Application data.

        Raises:
            ApplicationConfigError: In case of invalide value from data.
        """
        if not isinstance(self.excludes, list):
            msg = "{obj}: 'excludes' argument must be a list."
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
            ))

        # Models are required but not for an application drain object
        if not self.models and self.is_drain is False:
            msg = "{obj}: 'models' must not be an empty value."
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
            ))

        # Filename must have a file extension to discover serialization format
        extension = Path(self.filename).suffix
        if not extension:
            msg = (
                "{obj}: Given file name '{filename}' must have a file extension to "
                "discover format."
            )
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
                filename=self.filename,
            ))
        # File extension must correspond to an allowed format
        else:
            # Remove leading dot
            extension = extension[1:]
            if extension not in AVAILABLE_FORMATS:
                msg = (
                    "{obj}: Given file name '{filename}' must use a file extension "
                    "from allowed formats: {formats}"
                )
                raise ApplicationConfigError(msg.format(
                    obj=self.__repr__(),
                    filename=self.filename,
                    formats=", ".join(AVAILABLE_FORMATS),
                ))


class DrainApplicationConfig(ApplicationConfig):
    """
    Special application to drain remaining models.

    Attributes:
        drain_excluded (boolean): TODO
    """
    CONFIG_ATTRS = [
        "name", "models", "excludes", "natural_foreign", "natural_primary", "comments",
        "filename", "is_drain", "drain_excluded",
    ]
    OPTIONS_ATTRS = [
        "models", "excludes", "natural_foreign", "natural_primary", "filename",
    ]

    def __init__(self, *args, **kwargs):
        self.drain_excluded = kwargs.pop("drain_excluded", False)

        super().__init__(*args, **kwargs)

        self.is_drain = True
        self.allow_drain = False
