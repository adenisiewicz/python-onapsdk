#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Service properties module."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Input:
    """Property input dataclass."""

    unique_id: str
    input_type: str
    name: str
    default_value: Optional[Any] = None


@dataclass
class Property:  # pylint: disable=too-many-instance-attributes
    """Service property dataclass."""

    service: "Service"
    unique_id: str
    name: str
    property_type: str
    parent_unique_id: str
    value: Optional[Any] = None
    description: Optional[str] = None
    get_input_values: Optional[List[Dict[str, str]]] = None

    @property
    def input(self) -> Input:
        """Property input.

        Returns property Input object.
            Returns None if property has no associated input.

        Raises:
            AttributeError: Input for given property does not exits.
                It shouldn't ever happen, but it's possible if after you
                get property object someone delete input.

        Returns:
            Input: Property input object.

        """
        if not self.get_input_values:
            return None
        try:
            return next(filter(lambda x: x.unique_id == self.get_input_values[0].get("inputId"),
                               self.service.inputs))
        except StopIteration:
            raise AttributeError("Property input does not exist")
