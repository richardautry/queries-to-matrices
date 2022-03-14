import logging

from rest_framework import viewsets
from django.db.models import ForeignKey
from typing import List


logger = logging.Logger("main")

# TODO: Make warning message more verbose include viewset name, maybe serializer name, and maybe parent vs. nested
WARNING_MSG = "WARNING: `%s` not found in prefetch_related_lookups! Query may not be optimized"


def get_warning_message(field_name, viewset_name, serializer_class_name):
    pass


def check_all_prefetch_related_names(prefetch_related_lookups, serializer_class, found_related_names: List[str] = None):
    if not found_related_names:
        found_related_names = []
    for declared_field_name, declared_serializer_class in serializer_class._declared_fields.items():
        if declared_field_name not in found_related_names:
            found_related_names.append(declared_field_name)
            found_related_field_name = declared_field_name in prefetch_related_lookups
            if not found_related_field_name:
                logger.warning(WARNING_MSG, declared_field_name)
            found_related_names = check_all_prefetch_related_names(prefetch_related_lookups, declared_serializer_class.child, found_related_names)
    return found_related_names


def check_prefetch_related(viewset_class):
    viewset_class_init = viewset_class.__init__

    def viewset_init(self, **kwargs):
        for field in self.serializer_class.Meta.model._meta.fields:
            if isinstance(field, ForeignKey):
                found_field_name = field.name in self.queryset._prefetch_related_lookups
                if not found_field_name:
                    logger.warning(WARNING_MSG, field.name)

        check_all_prefetch_related_names(self.queryset._prefetch_related_lookups, self.serializer_class)

        return viewset_class_init(self, **kwargs)

    viewset_class.__init__ = viewset_init
    return viewset_class
