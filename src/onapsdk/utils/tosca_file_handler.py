#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring
"""Utils class."""
import json
import string
import random
import oyaml as yaml

from onapsdk.utils.jinja import jinja_env

# ----------------------------------------------------------
#
#               YAML UTILS
#
# -----------------------------------------------------------
def get_parameter_from_yaml(parameter, config_file):
    """
    Get the value of a given parameter in file.yaml.

    Parameter must be given in string format with dots
    Example: general.openstack.image_name
    :param config_file: yaml file of configuration
    :return: the value of the parameter
    """
    with open(config_file) as my_file:
        file_yaml = yaml.safe_load(my_file)
    my_file.close()
    value = file_yaml

    # Ugly fix as workaround for the .. within the params in the yaml file
    ugly_param = parameter.replace("..", "##")
    for element in ugly_param.split("."):
        value = value.get(element.replace("##", ".."))
        if value is None:
            raise ValueError("Parameter %s not defined" % parameter)

    return value


def get_model_from_tosca(tosca_file):
    """
    Retrieve Model from Tosca file.
    Else extract service, vnf and module models from the Tosca file

    : param the path of the tosca file
    """
    template_service = jinja_env().get_template(
        'service_instance_model_info.json.j2')
    data = {}
    # Get service instance model
    data['service_instance'] = json.loads(template_service.render(
        model_invariant_id=get_parameter_from_yaml("metadata.invariantUUID",
                                                   tosca_file),
        model_name_version_id=get_parameter_from_yaml("metadata.UUID",
                                                      tosca_file),
        model_name=get_parameter_from_yaml("metadata.name", tosca_file),
        model_version="1.0"))

    # Get VNF instance model
    data['vnf_instance'] = {}

    # Get VF module model
    data['vf_module'] = {}
    return data

def random_string_generator(size=6,
                            chars=string.ascii_uppercase + string.digits):
    """
    Get a random String for VNF.

    6 alphanumerical char for CI (to get single instances)
    :return: a random sequence of 6 characters
    """
    return ''.join(random.choice(chars) for _ in range(size))
