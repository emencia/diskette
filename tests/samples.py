"""
Sample application definitions to cover almost all corner case with options

.. Note:: This does not define any existing models, these are just dummy apps
"""

SAMPLE_APPS = [
    ("Blog", {
        "models": "blog",
    }),

    ("Tags", {
        "natural_foreign": True,
        "natural_primary": True,
        "models": "tags",
    }),

    ("Authors", {
        "models": ["authors.user", "authors.pin"],
        "excludes": ["authors.pin"],
    }),

    ("Contacts", {
        "models": ["contacts"],
        "excludes": ["contacts.token"],
    }),

    ("Cart", {
        "models": ["cart.item", "cart.payment"],
        "excludes": ["cart.payment"],
        "allow_drain": True,
    }),

    ("Pages", {
        "comments": "Lorem ipsum",
        "natural_foreign": True,
        "natural_primary": True,
        "models": ["pages"],
        "filename": "cmspages.json",
        "excludes": ["pages.revision"],
        "allow_drain": True,
    }),
]


# Temporary sample for full drain options until documented
# TODO: To remove
DRAIN_SAMPLE = [
    ("Drain", {
        # Define as an application drain
        "is_drain": True,
        "comments": "Lorem ipsum",
        "natural_foreign": True,
        "natural_primary": True,
        "filename": "drain.json",
        # Drain can specify some excludes itself
        "excludes": ["site"],
        # Allow to drain application excluded which allow it
        "drain_excluded": True,
    }),
]
