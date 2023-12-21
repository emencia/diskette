from pathlib import Path

from django.utils.text import slugify

from ..exceptions import ApplicationModelError

from .defaults import DEFAULT_FORMAT, AVAILABLE_FORMATS


class ApplicationModel:
    """
    Application model to validate and store application details.

    Arguments:
        name (string):
        models (list):

    Keyword Arguments:
        filename (string): The filename to use if application dump is to be written in
            a file. The filename also determine the format used to dump data. If you
            want another format that the default one you will have to define
            it from the filename even you don't plan to write dump to a file.
            Finally if not given, the filename will be automatically defined with
            slugified ``name`` with default format.
        excludes (list): The list of excluded models that won't be collected into the
            application dump.
        natural_foreign (boolean):
        natural_primary (boolean):
        comments (string): Free text which is not used from manager or serializer.
        allow_drain (boolean): If True, the application explicitely allows to drain
            its excluded models. If False, the application won't allow to drain them.
            Default is False to avoid implicit draining of data that may not be
            wanted.
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
        Returns Application options suitable for dumpdata.

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
            ApplicationModelError: In case of invalide value from data.
        """
        if not isinstance(self.excludes, list):
            msg = "{obj}: 'excludes' argument must be a list."
            raise ApplicationModelError(msg.format(
                obj=self.__repr__(),
            ))

        # Models are required but not for an application drain object
        if not self.models and self.is_drain is False:
            msg = "{obj}: 'models' must not be an empty value."
            raise ApplicationModelError(msg.format(
                obj=self.__repr__(),
            ))

        # Filename must have a file extension to discover serialization format
        extension = Path(self.filename).suffix
        if not extension:
            msg = (
                "{obj}: Given file name '{filename}' must have a file extension to "
                "discover format."
            )
            raise ApplicationModelError(msg.format(
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
                raise ApplicationModelError(msg.format(
                    obj=self.__repr__(),
                    filename=self.filename,
                    formats=", ".join(AVAILABLE_FORMATS),
                ))


class ApplicationDrainModel(ApplicationModel):
    """
    Special application to drain remaining models.
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
