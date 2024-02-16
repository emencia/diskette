from pathlib import Path

from django.apps import apps, AppConfig
from django.db import models
from django.utils.text import slugify

from ...exceptions import ApplicationConfigError, AppModelResolverError
from ..defaults import DEFAULT_FORMAT, AVAILABLE_FORMATS

from .resolver import AppModelResolverAbstract


class ApplicationConfig(AppModelResolverAbstract):
    """
    Application model to validate and store application details.

    TODO: Another name would better to avoid mental clash with Django "AppConfig".
    ApplicationModel (+2) ? ApplicationDataDef (0)? ApplicationDefinition (+3) ?
    DataDefinition (+3) ?

    Arguments:
        name (string): Application name, almost anything but it may be slugified for
            internal usages so avoid too much longer text and special characters.
        models (list): List of labels. A label is either an application label like
            ``auth`` or a full model label like ``auth.user``. Labels are validated,
            they must exists in Django application registry.

    Keyword Arguments:
        filename (string): The filename to use if application dump is to be written in
            a file. The filename also determine the format used to dump data. If you
            want another format that the default one you will have to define
            it from the filename even you don't plan to write dump to a file.
            Finally if not given, the filename will be automatically defined with
            slugified ``name`` with default format.
        excludes (list): The list of excluded model labels that won't be collected
            into the application dump. Currently, the excluded labels are not
            validated.
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
        self._models = [models] if isinstance(models, str) else models
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

    @property
    def models(self):
        """
        List all fully qualified model labels involved implicitely and explicitely from
        given ``models`` argument.
        """
        return self.resolve_labels(self._models, excludes=self.excludes)

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

    def is_valid_excludes(self, labels):
        """
        Validate given labels are fully qualified.

        Fully qualified label is made of two non empty name parts divided by a dot
        like ``foo.bar``.

        Arguments:
            labels (list): List of label to validate.

        Returns:
            list: A list of invalid labels.
        """
        invalids = [
            pattern
            for pattern in labels
            if (
                len(pattern.split(".")) < 2 or
                pattern.startswith(".") or
                pattern.endswith(".")
            )
        ]

        return invalids

    def validate(self):
        """
        Validate Application data.

        Raises:
            ApplicationConfigError: In case of invalid values from options.
        """
        if not isinstance(self.excludes, list):
            msg = "{obj}: 'excludes' argument must be a list."
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
            ))
        else:
            errors = self.is_valid_excludes(self.excludes)
            if errors:
                msg = (
                    "{obj}: 'excludes' argument can only contains fully qualified "
                    "labels (like 'foo.bar') these ones are invalid: {labels}"
                )
                raise ApplicationConfigError(msg.format(
                    obj=self.__repr__(),
                    labels=", ".join(errors),
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

        # Try to resolve models that should raise exceptions for invalid labels
        self.resolve_labels(self.models)


class DrainApplicationConfig(ApplicationConfig):
    """
    Special application to drain remaining models.

    Attributes:
        drain_excluded (boolean): TODO: Should define if Drain cares of excluded model
            from app with 'allow_drain' or not. It is useful to have a drain which only
            care about undefined apps and assume excludes from defined apps are totally
            to ignore.
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
