from pathlib import Path

from django.utils.text import slugify

from ..exceptions import ApplicationModelError


class ApplicationModel:
    """
    Application model to validate and store application details.
    """
    DEFAULT_FORMAT = "json"
    AVAILABLE_FORMATS = ("json", "jsonl", "xml", "yaml")

    def __init__(self, name, models, filename=None, exclude=None,
                 natural_foreign=False, natural_primary=False, comments=None):
        self.name = name
        self.models = [models] if isinstance(models, str) else models
        self.exclude = exclude or []
        self.natural_foreign = natural_foreign
        self.natural_primary = natural_primary
        self.comments = comments
        self.filename = filename or self.get_filename()

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
        return slugify(self.name) + "." + (format_extension or self.DEFAULT_FORMAT)

    def as_dict(self, named=False, commented=False):
        """
        Returns Application data as a dictionnary.

        Keyword Arguments:
            name (boolean): To include or not the name into the dict.
            commented (boolean): To include or not the comments into the dict.

        Returns
            dict: Application data.
        """
        data = {
            "models": self.models,
            "exclude": self.exclude,
            "natural_foreign": self.natural_foreign,
            "natural_primary": self.natural_primary,
            "filename": self.filename,
        }

        if named:
            data.update({"name": self.name})

        if commented:
            data.update({"comments": self.comments})

        return data

    def validate(self):
        """
        Validate Application data.

        Raises:
            ApplicationModelError: In case of invalide value from data.
        """
        if not isinstance(self.exclude, list):
            msg = "{obj}: 'exclude' argument must be a list."
            raise ApplicationModelError(msg.format(
                obj=self.__repr__(),
            ))

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
        else:
            # Remove leading dot
            extension = extension[1:]
            if extension not in self.AVAILABLE_FORMATS:
                msg = (
                    "{obj}: Given file name '{filename}' must use a file extension "
                    "from allowed formats: {formats}"
                )
                raise ApplicationModelError(msg.format(
                    obj=self.__repr__(),
                    filename=self.filename,
                    formats=", ".join(self.AVAILABLE_FORMATS),
                ))
