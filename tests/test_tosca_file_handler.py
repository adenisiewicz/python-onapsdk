#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import logging
import os
import os.path
import unittest

from onapsdk.utils.jinja import jinja_env
import onapsdk.utils.tosca_file_handler as onap_test_utils

__author__ = "Morgan Richomme <morgan.richomme@orange.com>"


class ToscaFileHandlerTestingBase(unittest.TestCase):

    """The super class which testing classes could inherit."""

    logging.disable(logging.CRITICAL)

    _root_path = os.getcwd().rsplit('/onapsdk')[0]
    _foo_path = "/src/onapsdk/templates/tosca_files/service-Foo-template.yml"


    def setUp(self):
        pass

    def test_get_parameter_from_yaml(self):
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

if __name__ == "__main__":
    # logging must be disabled else it calls time.time()
    # what will break these unit tests.
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
