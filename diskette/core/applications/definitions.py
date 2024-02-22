from pathlib import Path

from django.apps import apps, AppConfig
from django.db import models
from django.utils.text import slugify

from ...exceptions import ApplicationConfigError, AppModelResolverError
from ..defaults import DEFAULT_FORMAT, AVAILABLE_FORMATS

from .store import get_appstore


appstore = get_appstore()


class ApplicationConfig:
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
        "name", "models", "excludes", "retention", "natural_foreign", "natural_primary",
        "comments", "filename", "is_drain", "allow_drain",
    ]
    OPTIONS_ATTRS = [
        "models", "excludes", "natural_foreign", "natural_primary", "filename",
    ]

    def __init__(self, name, models=[], excludes=None, natural_foreign=False,
                 natural_primary=False, comments=None, filename=None,
                 is_drain=None, allow_drain=False):
        self.name = name
        self._models = [models] if isinstance(models, str) else models
        self._excludes = excludes or []
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
        List all fully qualified model labels to include, either implicitely and
        explicitely from given ``models`` argument.

        NOTE: models, excludes and retention attributes may be cached since they have
        no reason to change.

        Returns:
            list: Fully qualified model labels.
        """
        return [
            model.label
            for model in appstore.get_models_inclusions(
                self._models, excludes=self._excludes
            )
        ]

    @property
    def excludes(self):
        """
        List all fully qualified model labels to exclude, either implicitely and
        explicitely from given ``_excludes`` argument.

        Returns:
            list: Fully qualified model labels.
        """
        return [
            model.label
            for model in appstore.get_models_exclusions(
                self._models, excludes=self._excludes
            )
        ]

    @property
    def retention(self):
        """
        List all fully qualified model labels that are not allowed to be drained from
        this application.

        Included models are never allowed to be drained and exclusions models may be
        allowed if ``allow_drain`` is enabled.

        Returns:
            list: Fully qualified model labels that won't be allowed to be drained.
                This means labels from ``models`` on defaut and possibly the
                ``excludes`` one also if application allows for drainage.
        """
        if not self.allow_drain:
            return self.models + self.excludes

        return self.models


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

    def validate_includes(self):
        """
        Validate include labels from ``_models`` attribute.
        """
        # Models are required but not for an application drain object
        if not self._models and self.is_drain is False:
            msg = "{obj}: 'models' must not be an empty value."
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
            ))

        unknow_apps, unknow_models = appstore.check_unexisting_labels(self._models)

        if len(unknow_apps) > 0:
            msg = (
                "{obj}: Some given app labels to include does not exists: {labels}"
            )
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
                labels=", ".join(unknow_apps),
            ))

        if len(unknow_models) > 0:
            msg = (
                "{obj}: Some given models labels to include does not exists: {labels}"
            )
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
                labels=", ".join(unknow_models),
            ))

    def validate_excludes(self):
        """
        Validate exclude labels from ``excludes`` attribute.
        """
        if not isinstance(self._excludes, list):
            msg = "{obj}: 'excludes' argument must be a list."
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
            ))
        else:
            errors = appstore.is_fully_qualified_labels(self._excludes)
            if errors:
                msg = (
                    "{obj}: 'excludes' argument can only contains fully qualified "
                    "labels (like 'foo.bar') these ones are invalid: {labels}"
                )
                raise ApplicationConfigError(msg.format(
                    obj=self.__repr__(),
                    labels=", ".join(errors),
                ))

        unknow_apps, unknow_models = appstore.check_unexisting_labels(self._excludes)

        if len(unknow_apps) > 0:
            msg = (
                "{obj}: Some given app labels to exclude does not exists: {labels}"
            )
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
                labels=", ".join(unknow_apps),
            ))

        if len(unknow_models) > 0:
            msg = (
                "{obj}: Some given models labels to exclude does not exists: {labels}"
            )
            raise ApplicationConfigError(msg.format(
                obj=self.__repr__(),
                labels=", ".join(unknow_models),
            ))

    def validate_filename(self):
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

    def validate(self):
        """
        Validate Application options.

        Raises:
            ApplicationConfigError: In case of invalid values from options.
        """
        self.validate_filename()
        self.validate_includes()
        self.validate_excludes()


class DrainApplicationConfig(ApplicationConfig):
    """
    Special application to drain remaining models from apps.

    On default a drain will dump anything that have not been defined from apps. Its
    base goal is to dump data from undefined applications.

    Attributes:
        drain_excluded (boolean): If enabled, the drain will accept to drain exclusion
            from applications which allow it. Else the drain will exclude also the
            application exclusion. Default is disabled.
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

        # Drain never allow for any inclusion
        self._models = []
        # Force as a drain only
        self.is_drain = True
        # It is not allowed to be drained itself
        self.allow_drain = False

    @property
    def excludes(self):
        """
        Just returns exclude labels as given since drain excludes are meaningful
        enough.

        Returns:
            list: Fully qualified model labels.
        """
        return self._excludes
