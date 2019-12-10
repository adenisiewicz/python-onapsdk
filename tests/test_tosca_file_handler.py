#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import logging
<<<<<<< HEAD
import json
import oyaml as yaml
=======
>>>>>>> 31e66f4b201b6fed0d5c0ca5b7752d6d3ab992f3
import os
import os.path
import unittest

from onapsdk.utils.jinja import jinja_env
<<<<<<< HEAD
import onapsdk.utils.tosca_file_handler as tosca_file_handler

=======
import onapsdk.utils.tosca_file_handler as onap_test_utils
>>>>>>> 31e66f4b201b6fed0d5c0ca5b7752d6d3ab992f3

__author__ = "Morgan Richomme <morgan.richomme@orange.com>"


class ToscaFileHandlerTestingBase(unittest.TestCase):

    """The super class which testing classes could inherit."""

    logging.disable(logging.CRITICAL)

    _root_path = os.getcwd().rsplit('/onapsdk')[0]
<<<<<<< HEAD
    _foo_path = _root_path +"/tests/data/service-Ubuntu16-template.yml"
=======
    _foo_path = "/src/onapsdk/templates/tosca_files/service-Foo-template.yml"
>>>>>>> 31e66f4b201b6fed0d5c0ca5b7752d6d3ab992f3


    def setUp(self):
        pass

    def test_get_parameter_from_yaml(self):
<<<<<<< HEAD
        with open(self._foo_path) as f:
            model = json.dumps(yaml.safe_load(f))
        param = tosca_file_handler.get_parameter_from_yaml(
            "metadata", model)
        self.assertEqual(param['name'], "ubuntu16")

    def test_get_wrong_parameter_from_yaml(self):
        with open(self._foo_path) as f:
            model = json.dumps(yaml.safe_load(f))
        with self.assertRaises(ValueError):
            tosca_file_handler.get_parameter_from_yaml(
                "wrong_parameter", model)

    def test_get_parameter_from_wrong_yaml(self):
        with self.assertRaises(FileNotFoundError):
            with open("wrong_path") as f:
                model = json.dumps(yaml.safe_load(f))
                tosca_file_handler.get_parameter_from_yaml(
                    "metadata", model)

    def test_get_random_string_generator(self):
        self.assertEqual(
            len(tosca_file_handler.random_string_generator()), 6)

    def test_get_vf_list_from_tosca_file(self):
        with open(self._foo_path) as f:
            model = json.dumps(yaml.safe_load(f))
        vf_list = tosca_file_handler.get_vf_list_from_tosca_file(model)
        self.assertEqual(vf_list[0], 'ubuntu16_VF')

    # def get_vf_list_from_tosca_file_wrong_model(self):
    #     with self.assertRaises(FileNotFoundError):
    #         tosca_file_handler.get_vf_list_from_tosca_file(
    #             self._root_path + "wrong_path")
=======
        param = onap_test_utils.get_parameter_from_yaml(
            "metadata", self._root_path + self._foo_path)
        self.assertEqual(param['name'], "vFW-service")

    def test_get_wrong_parameter_from_yaml(self):
        with self.assertRaises(ValueError):
            onap_test_utils.get_parameter_from_yaml(
                "wrong_parameter", self._root_path + self._foo_path)

    def test_get_parameter_from_wrong_yaml(self):
        with self.assertRaises(FileNotFoundError):
            onap_test_utils.get_parameter_from_yaml(
                "metadata", "wrong_path")

    def test_get_random_string_generator(self):
        self.assertEqual(
            len(onap_test_utils.random_string_generator()),
            6)

    def test_get_model_from_tosca(self):
        service_model = onap_test_utils.get_model_from_tosca(
            self._root_path + self._foo_path)
        self.assertEqual(
            service_model['service_instance']['modelInfo']['modelType'],
            "service")

    def test_get_model_from_tosca_wrong_name(self):
        with self.assertRaises(FileNotFoundError):
            onap_test_utils.get_model_from_tosca(
                self._root_path + "wrong_path")
>>>>>>> 31e66f4b201b6fed0d5c0ca5b7752d6d3ab992f3

if __name__ == "__main__":
    # logging must be disabled else it calls time.time()
    # what will break these unit tests.
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
