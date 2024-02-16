from pathlib import Path

from django.apps import apps, AppConfig
from django.db import models
from django.utils.text import slugify

from ...exceptions import ApplicationConfigError, AppModelResolverError


class AppModelResolverAbstract:
    """
    Abstract for methods to resolve model labels from applications
    """
    def normalize_model_name(self, model, app=None):
        """
        Return normalized name for a model.

        DEPRECATED: Ported as DjangoAppLookupStore.normalize_label

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
        Return model labels for given application.

        DEPRECATED: Ported as DjangoAppLookupStore.get_app_model_labels

        Returns:
            list: Fully qualified model labels formatted as ``APPNAME.MODELNAME``.
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

        DEPRECATED: Ported as DjangoAppLookupStore.get_all_model_labels

        Returns:
            list:
        """
        collected = []

        for app in apps.get_app_configs():
            names = self.get_app_models(app)

            if names:
                collected.extend(names)

        return collected

    def filter_out_excludes(self, excludes=None):
        """
        Return a callable to be used to filter out excluded labels from given iterable.

        Returns:
            list:
        """
        def _curry(item):
            return True if not excludes else item not in excludes

        return _curry

    def resolve_labels(self, labels, excludes=None):
        """
        Resolve model names for given labels.

        Arguments:
            labels(string or list): Each label can be either model labels (as a string
                for a single one or a list for more) or application labels.

                Application label
                    This will be resolved to a list of names for all of its models, so
                    its useful to select all app models.

                Model label
                    Also known as a *fully qualified label*. We use it unchanged
                    without resolution. so its useful to explicitely define some
                    models, the ones that are not defined will be ignored.

                    A Model label must be in the form "APP.MODEL" because without the
                    second part after the dot is assumed as an Application label.

        Raises:
            LookupError: This is raised by Django application framework when an
                application label does not exist in application registry. We let it
                raises to keep a proper stacktrace on purpose.

        Returns:
            list: List of resolved model names from given labels.
        """
        names = []

        # Ensure we allways have a list
        labels = [labels] if isinstance(labels, str) else labels

        for label in labels:
            # Try to parse item as a fully qualified label
            try:
                app_label, model_label = label.split(".")
            # If not a fully qualified label assume it is an application label and add
            # all models in their original registered order
            except ValueError:
                names.extend(self.get_app_models(label))
            else:
                # Add the fully qualified label
                # NOTE: This won't preserve original model registered order, instead
                # it follows the definition order, it may not be safe for dump
                # restoration
                names.append(self.normalize_model_name(model_label, app=app_label))

        return list(filter(self.filter_out_excludes(excludes), names))
