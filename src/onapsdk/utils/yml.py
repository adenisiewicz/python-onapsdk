#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring
"""Yaml module"""

from typing import Any
import oyaml


def get_parameter_from_yaml(parameter: str, config_file: str) -> Any:
    """
    Get the value of a given parameter in file.yaml.

    Parameter must be given in string format with dots

    Args:
        parameter (str): the parameter to find
        config_file (str): the path of config file to parse

    Returns:
        Any: the value of the parameter

    Example:
        >>> import yaml
        >>> dict = {'global': {'setup': {'version': 'v1.0'}}}
        >>> file = open("/tmp/test.yaml", "w")
        >>> file.write(yaml.dump(dict))
        35
        >>> file.close()
        >>> get_parameter_from_yaml('global.setup.version', "/tmp/test.yaml")
        'v1.0'
        >>> get_parameter_from_yaml('global.setup', "/tmp/test.yaml")
        {'version': 'v1.0'}
        >>> get_parameter_from_yaml('global.other.version', "/tmp/test.yaml")
        Traceback (most recent call last):
            ...
        ValueError: Parameter global.other.version not defined
        >>> get_parameter_from_yaml('global.setup', "/tmp/other.yaml")
        Traceback (most recent call last):
            ...
        FileNotFoundError: [Errno 2] No such file or directory: '/tmp/other.yaml'

    """
    with open(config_file) as my_file:
        file_yaml = oyaml.safe_load(my_file)
    my_file.close()
    value = file_yaml

    # Ugly fix as workaround for the .. within the params in the yaml file
    ugly_param = parameter.replace("..", "##")
    for element in ugly_param.split("."):
        value = value.get(element.replace("##", ".."))
        if value is None:
            raise ValueError("Parameter %s not defined" % parameter)

    return value
