import json

from datalookup import Dataset

from django.apps import apps, AppConfig
from django.db import models

from diskette.exceptions import (
    DoesNotExistsFromAppstore, MultipleObjectExistsFromAppstore
)


class DjangoAppLookupStore:
    """
    Django application store collects applications and store them with their useful
    parameters.

    .. _Django apps: https://docs.djangoproject.com/en/stable/ref/applications/

    This registry is built on top of `Django apps`_ to include more useful methods to
    perform queries alike with Django ORM. It helps to find detailed inclusions and
    exclusions with application models.

    Attributes:
        registry (Dataset): The store registry built as a ``datalookup.Dataset``.

    Keyword Arguments:
        registry (list): List of dictionnaries, each dictionnary is an application
            item with its parameters. If not given, it will be filled automatically
            from enabled applications using ``django.apps``.

    """
    def __init__(self, registry=None):
        self._registry = registry or self.get_registry()
        self.registry = Dataset(self._registry)

    def as_dict(self):
        """
        Return the store items with their parameters as a dictionnary.

        Returns:
            dict: Store items as a dictionnary.
        """
        return self._registry

    def as_json(self):
        """
        Return the store items with their parameters as JSON.

        Returns:
            string: Store items as JSON.
        """
        return json.dumps(self.as_dict())

    @classmethod
    def normalize_label(cls, model, app=None):
        """
        Return normalized name for a model or FQM label.

        Arguments:
            model (string or object): Model name as a string or an object that inherits
                from ``django.db.models.base.ModelBase``.

        Keyword Arguments:
            app (string or object): Either a model object, AppConfig object or a
                string for an application label.

        Returns:
            string: A fully qualified model name composed from app name and model name.
        """
        if app and isinstance(app, AppConfig):
            app = app.label

        if isinstance(model, models.base.ModelBase):
            model = model.__name__

        if not app:
            return model

        return app + "." + model

    @classmethod
    def is_fully_qualified_labels(cls, labels):
        """
        Validate given labels are fully qualified model labels.

        Arguments:
            labels (list): List of label to validate.

        Returns:
            list: A list of invalid labels.
        """
        # NOTE: We currently don't bother of label that are divided (by a dot) in more
        # than two parts, since we are not sure Django would allows labels on three or
        # more parts
        return [
            pattern
            for pattern in labels
            if (
                len(pattern.split(".")) < 2 or
                pattern.startswith(".") or
                pattern.endswith(".")
            )
        ]

    def get_registry_app_models(self, app_id, app):
        """
        Return model labels for given application.

        Internally used to build appstore registry.

        Arguments:
            app_id (integer): An unique id to represent related application.
            app (AppConfig): The application object from Django apps.

        Returns:
            list: A list of dictionnaries for models. Model dictionnary will contains
            the following items:

            id
                A simple integer built from the loop, since it is only done internally
                it should be ensured to be unique.
            app_id
                Given application id.
            unique_id
                A special field to help for ordering on models since datalookup does
                not provide a way to do this. This is a join of app id and model id,
                both formatted on 4 digits filled by zero.
            app
                Application label.
            name
                Model class name.
            object
                Model class.
            label
                Fully qualified model label.
        """
        return [
            {
                "id": i,
                "app_id": app_id,
                "unique_id": "{app}{model}".format(
                    app=str(app_id).zfill(4),
                    model=str(i).zfill(4),
                ),
                "app": app.label,
                "name": model.__name__,
                "object": model,
                "label": self.normalize_label(model, app=app),
            }
            for i, model in enumerate(app.get_models(
                include_auto_created=True,
                include_swapped=True
            ), start=1)
        ]

    def get_registry(self):
        """
        Store all model labels from enabled applications into a registry.

        Returns:
            list: A list of dictionnaries for applications. Application dictionnary
            will contains the following items:

            id
                A simple integer built from the loop, since it is only done internally
                it should be ensured to be unique.
            verbose_name
                Application verbose name.
            label
                Application label.
            pythonpath
                Python path to the application itself.
            models
                A list of application models as returned from method
                ``DjangoAppLookupStore.get_registry_app_models``.
        """
        collected = []
        i = 1

        for app in apps.get_app_configs():
            names = self.get_registry_app_models(i, app)

            if names:
                collected.append({
                    "id": i,
                    "verbose_name": str(app.verbose_name),
                    "label": app.label,
                    "pythonpath": app.name,
                    "models": names,
                })
                i += 1

        return collected

    def get_app(self, label):
        """
        Getter to retrieve a single application from a label.

        Arguments:
            label (string): Application label.

        Raises:
            MultipleObjectExistsFromAppstore: If there is more than one application
                object with the same label. This is something that should never happen
                because of how Django manage applications.
            DoesNotExistsFromAppstore: If there is not any application with the given
                label.

        Returns:
            node: Datalookup node for retrieved application.
        """
        app = self.registry.filter(label__exact=label)
        length = len(app)

        if length > 1:
            raise MultipleObjectExistsFromAppstore(
                "Given app label '{app}' return multiple objects ({length})".format(
                    app=label,
                    length=length,
                )
            )
        elif length == 0:
            raise DoesNotExistsFromAppstore(
                "No app object exists for given label: '{app}'".format(
                    app=label,
                )
            )

        return app[0]

    def get_model(self, label):
        """
        Getter to retrieve a single application model from a label.

        Arguments:
            label (string): Fully qualified model label.

        Raises:
            MultipleObjectExistsFromAppstore: If there is more than one application
                object with the same label. This is something that should never happen
                because of how Django manage applications.
            DoesNotExistsFromAppstore: If there is not any application with the given
                label.

        Returns:
            node: Datalookup node for retrieved application.
        """
        model = self.registry.filter_related("models", label__exact=label)
        length = len(model)

        if length > 1:
            raise MultipleObjectExistsFromAppstore(
                "Given model label '{model}' return multiple objects ({length})".format(
                    model=label,
                    length=length,
                )
            )
        elif length == 0:
            raise DoesNotExistsFromAppstore(
                "No model object exists for given label: '{model}'".format(
                    model=label,
                )
            )

        return model[0]

    def get_app_model_labels(self, app):
        """
        Return model labels for given application.

        Arguments:
            app (sring): Application label.

        Returns:
            list: Fully qualified model labels.
        """
        return [
            model.label
            for model in self.registry.filter(
                label__exact=app
            ).filter_related("models")
        ]

    def get_all_model_labels(self):
        """
        Return all model labels from all enabled applications.

        Returns:
            list: Fully qualified model labels.
        """
        return [
            model.label
            for model in self.registry.filter_related("models")
        ]

    def check_unexisting_labels(self, labels):
        """
        Check if given labels exists as app or models in store.

        Arguments:
            labels (list): A list of application or FQM label (string) to check.

        Returns:
            Tuple: Respectively a list of not found apps and a list of not found
            models.
        """
        unknow_apps = []
        unknow_models = []

        # Ensure we allways have a list
        labels = [labels] if isinstance(labels, str) else labels

        for label in labels:
            # Try to parse item as a fully qualified label
            try:
                app_label, model_label = label.split(".")
            # If not a fully qualified label assume it is an application label and add
            # all models in their original registered order
            except ValueError:
                try:
                    self.get_app(label)
                except DoesNotExistsFromAppstore:
                    unknow_apps.append(label)
            else:
                try:
                    self.get_model(label)
                except DoesNotExistsFromAppstore:
                    unknow_models.append(label)

        return unknow_apps, unknow_models

    def get_models_inclusions(self, labels, excludes=None):
        """
        Returns model nodes for inclusions.

        Arguments:
            labels (string or list): A list of App label (string), fully qualified
                model labels (string) or AppConfig.

        Keyword Arguments:
            excludes (list): List of fully qualified model labels to exclude.

        Returns:
            list: List of Datalookup nodes.
        """
        names = []

        # Ensure we allways have a list
        labels = [labels] if isinstance(labels, str) else labels
        excludes = excludes or []
        excludes = [excludes] if isinstance(excludes, str) else excludes

        for label in labels:
            if isinstance(label, AppConfig):
                label = label.label
            # Try to parse item as a fully qualified label
            try:
                app_label, model_label = label.split(".")
            # If not a fully qualified label assume it is an application label and add
            # all models in their original registered order
            except ValueError:
                # Append all models that are not excluded explicitely
                names.extend([
                    model
                    for model in self.get_app(label).models
                    if model.label not in excludes
                ])
            else:
                # Add the fully qualified label if not excluded explicitely
                if self.normalize_label(model_label, app=app_label) not in excludes:
                    names.append(self.get_model(label))

        # Finally order on model unique id
        return sorted(names, key=lambda item: item.unique_id)

    def get_models_exclusions(self, labels, excludes=None):
        """
        Returns model nodes for exclusions.

        Exclusion gather the explicit exclude labels and the intersection between
        inclusions and missing models related to implied app from inclusion labels.

        Arguments:
            labels (string or list): App label or fully qualified model labels.

        Keyword Arguments:
            excludes (list): List of fully qualified model labels.

        Returns:
            list: List of Datalookup nodes.
        """
        names = []

        # Ensure we allways have a list
        excludes = [excludes] if isinstance(excludes, str) else excludes
        excludes = excludes or []

        # Get model nodes for inclusion from given labels
        model_items = self.get_models_inclusions(labels, excludes=excludes)

        exclude_apps = [label.split(".")[0] for label in excludes]

        # Get involved app labels from resolved inclusions and exclusions, enforcing
        # unique items
        involved_apps = list(set([item.app for item in model_items] + exclude_apps))

        # Queryset is related to models but limited on involved apps
        q = self.registry.filter(label__in=involved_apps).filter_related("models")

        # Finally reject inclusions
        names = q.exclude(label__in=[v.label for v in model_items])

        return sorted(names, key=lambda item: item.unique_id)
