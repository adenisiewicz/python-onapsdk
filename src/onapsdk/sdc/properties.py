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


class Property:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """Service property class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 property_type: str,
                 description: Optional[str] = None,
                 unique_id: Optional[str] = None,
                 parent_unique_id: Optional[str] = None,
                 sdc_resource: Optional["SdcResource"] = None,
                 value: Optional[Any] = None,
                 get_input_values: Optional[List[Dict[str, str]]] = None,
                 declare_input: Optional[bool] = False) -> None:
        """Property class initialization.

        Args:
            property_type (str): [description]
            description (Optional[str], optional): [description]. Defaults to None.
            unique_id (Optional[str], optional): [description]. Defaults to None.
            parent_unique_id (Optional[str], optional): [description]. Defaults to None.
            sdc_resource (Optional[, optional): [description]. Defaults to None.
            value (Optional[Any], optional): [description]. Defaults to None.
            get_input_values (Optional[List[Dict[str, str]]], optional): [description].
                Defaults to None.
            declare_input (Optional[bool], optional): [description]. Defaults to False.
        """
        self.name: str = name
        self.property_type: str = property_type
        self.description: str = description
        self.unique_id: str = unique_id
        self.parent_unique_id: str = parent_unique_id
        self.sdc_resource: "SdcResource" = sdc_resource
        self.value: Any = value
        self.get_input_values: List[Dict[str, str]] = get_input_values
        self.declare_input: bool = declare_input

    def __repr__(self) -> str:
        """Property object human readable representation.

        Returns:
            str: Property human readable representation

        """
        return f"Property(name={self.name}, property_type={self.property_type})"

    @property
    def input(self) -> Input:
        """Property input.

        Returns property Input object.
            Returns None if property has no associated input.

        Raises:
            AttributeError: Input has no associated SdcResource

            AttributeError: Input for given property does not exits.
                It shouldn't ever happen, but it's possible if after you
                get property object someone delete input.

        Returns:
            Input: Property input object.

        """
        if not self.sdc_resource:
            raise AttributeError("Property has no associated SdcResource")
        if not self.get_input_values:
            return None
        try:
            return next(filter(lambda x: x.unique_id == self.get_input_values[0].get("inputId"),
                               self.sdc_resource.inputs))
        except StopIteration:
            raise AttributeError("Property input does not exist")