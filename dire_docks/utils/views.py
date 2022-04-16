import logging

from typing import List, Tuple
from rest_framework.serializers import PrimaryKeyRelatedField, ModelSerializer, ListSerializer


logger = logging.Logger("main")

# TODO: Make warning message more verbose include viewset name, maybe serializer name, and maybe parent vs. nested
WARNING_MSG = "WARNING: `%s` not found in prefetch_related_lookups! Query may not be optimized"


def get_warning_message(field_name, viewset_name, serializer_class_name):
    pass


def get_parsed_nested_lookups(prefetch_related_lookups: Tuple[str]):
    extracted_field_names = []
    for lookup in prefetch_related_lookups:
        for field_name in lookup.split("__"):
            if field_name not in extracted_field_names:
                extracted_field_names.append(field_name)
    return extracted_field_names


def check_all_prefetch_related_names(
        prefetch_related_lookups,
        serializer_class,
        prefetch_related_name: str = None,
        found_related_names: List[str] = None
):
    if not found_related_names:
        found_related_names = []
    for declared_field_name, declared_serializer_class in serializer_class._declared_fields.items():
        if prefetch_related_name:
            prefetch_related_prefix = prefetch_related_name
        else:
            prefetch_related_prefix = declared_field_name
        if isinstance(declared_serializer_class, ModelSerializer) or isinstance(declared_serializer_class, ListSerializer):
            found_related_names = check_all_prefetch_related_names(
                prefetch_related_lookups,
                declared_serializer_class.child,
                prefetch_related_prefix,
                found_related_names
            )
            if declared_field_name not in found_related_names:
                found_related_names.append(declared_field_name)
                if (
                        declared_field_name not in prefetch_related_lookups and
                        declared_field_name not in get_parsed_nested_lookups(prefetch_related_lookups)
                ):
                    logger.warning(WARNING_MSG, declared_field_name)
    if prefetch_related_name:
        prefetch_related_prefix = prefetch_related_name
    else:
        prefetch_related_prefix = None
    # We need to check `prefetch_related_fields` at all levels, but this does NOT trigger recursion
    if hasattr(serializer_class.Meta, "prefetch_related_fields"):
        for prefetch_related_field in serializer_class.Meta.prefetch_related_fields:
            if prefetch_related_prefix:
                prefetch_related_field = "__".join([prefetch_related_prefix, prefetch_related_field])

            if prefetch_related_field not in found_related_names:
                found_related_names.append(prefetch_related_field)
                if prefetch_related_field not in prefetch_related_lookups:
                    logger.warning(WARNING_MSG, prefetch_related_field)
    return found_related_names


def check_prefetch_related(viewset_class):
    """
    Decorator for checking that any nested elements in a serializer are represented in the
    `prefetch_related` declaration of a queryset.

    NOTE: `prefetch_related_fields` can be added to the `Meta` of a serializer to tell this checker
    what/where to look
    """
    viewset_class_init = viewset_class.__init__

    def viewset_init(self, **kwargs):
        for declared_field_name, declared_serializer in self.serializer_class._declared_fields.items():
            if isinstance(declared_serializer, PrimaryKeyRelatedField):
                if declared_serializer.source not in self.queryset._prefetch_related_lookups:
                    logger.warning(WARNING_MSG, declared_field_name)

        check_all_prefetch_related_names(self.queryset._prefetch_related_lookups, self.serializer_class)

        return viewset_class_init(self, **kwargs)

    viewset_class.__init__ = viewset_init
    return viewset_class
