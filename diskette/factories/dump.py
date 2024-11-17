import factory

from ..models import DumpFile


class DumpFileFactory(factory.django.DjangoModelFactory):
    """
    Factory to create instance of a DumpFile.
    """
    processed = None
    deprecated = False
    status = 0
    with_data = True
    with_storage = True
    path = ""
    checksum = ""
    size = 0
    logs = ""

    class Meta:
        model = DumpFile
        skip_postgeneration_save = True
