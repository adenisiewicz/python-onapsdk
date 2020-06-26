#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test clamp module."""

from unittest import mock
from unittest.mock import MagicMock

import json
import pytest

from onapsdk.clamp import Clamp, LoopInstance
from onapsdk.service import Service

#examples
TEMPLATES = [
    {
        "name" : "test_template",
        "modelService" : {
            "serviceDetails" : {
                "name" : "test"
            }
        }
    }
]

POLICIES = [
    {
        "policyModelType" : "onap.policies.controlloop.Test",
        "version" : "1.0.0",
        "policyAcronym" : "Test",
        "createdDate" : "2020-04-30T09:03:30.362897Z",
        "updatedDate" : "2020-04-30T09:03:30.362897Z",
        "updatedBy" : "Not found",
        "createdBy" : "Not found"
    }
]

LOOP_DETAILS = {
    "name" : "LOOP_test",
    "operationalPolicies" : [
        {
            "name" : "MICROSERVICE_test"
        }
    ],
    "microServicePolicies" : [
        {
            "name" : "MICROSERVICE_test"
        }
    ]
}
#end of examples


def test_initialization():
    """Class initialization test."""
    clamp = Clamp()
    assert isinstance(clamp, Clamp)


@mock.patch.object(Clamp, 'send_message_json')
def test_check_loop_template(mock_send_message_json):
    """Test Clamp's class method."""
    svc = Service(name='test')
    mock_send_message_json.return_value = TEMPLATES
    template = Clamp.check_loop_template(service=svc)
    mock_send_message_json.assert_called_once_with('GET',
                                                   'Get Loop Templates',
                                                   (f"{Clamp.base_url()}/templates/"),
                                                   Clamp.pkcs12_filename,
                                                   Clamp.pkcs12_password)
    assert template == "test_template"


@mock.patch.object(Clamp, 'send_message_json')
def test_check_loop_template_none(mock_send_message_json):
    """Test Clamp's class method."""
    svc = Service(name='test')
    mock_send_message_json.return_value = {}
    with pytest.raises(ValueError):
        template = Clamp.check_loop_template(service=svc)
        assert template is None


@mock.patch.object(Clamp, 'send_message_json')
def test_check_policies(mock_send_message_json):
    mock_send_message_json.return_value = POLICIES
    with pytest.raises(ValueError):
        exists = Clamp.check_policies(policy_name="Test")
        mock_send_message_json.\
            assert_called_once_with('GET',
                                    'Get stocked policies',
                                    (f"{Clamp.base_url()}/policyToscaModels/"),
                                    Clamp.pkcs12_filename,
                                    Clamp.pkcs12_password)
        assert exists 


def test_cl_initialization():
    """Class initialization test."""
    loop = LoopInstance(template="template", name="LOOP_name", details={})
    assert isinstance(loop, LoopInstance)


@mock.patch.object(LoopInstance, 'send_message_json')
def test_create(mock_send_message_json):
    """Test Loop instance creation."""
    instance = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = LOOP_DETAILS
    instance.create()
    mock_send_message_json.assert_called_once_with('POST', 'Create Loop Instance',
         (f"{instance.base_url}/loop/create/test?templateName=template"),
         instance.pkcs12_filename,
         instance.pkcs12_password)
    assert instance.name == "LOOP_test"
    assert len(instance.details["microServicePolicies"]) > 0


@mock.patch.object(LoopInstance, 'send_message_json')
def test_add_operational_policy(mock_send_message_json):
    """Test adding an op policy."""
    loop = LoopInstance(template="template", name="LOOP_test", details={})
    loop.details = {
        "name" : "LOOP_test",
        "operationalPolicies" : [],
        "microServicePolicies" : [
            {
                "name" : "MICROSERVICE_test"
            }
        ]
    }
    mock_send_message_json.return_value = LOOP_DETAILS
    loop.add_oprational_policy(policy_type="FrequencyLimiter", policy_version="1.0.0")
    mock_send_message_json.assert_called_once_with('PUT', 'Create Operational Policy',
        (f"{loop.base_url}/loop/addOperationaPolicy/{loop.name}/policyModel/FrequencyLimiter/1.0.0"),
        loop.pkcs12_filename,
        loop.pkcs12_password)
    assert loop.name == "LOOP_test"
    assert len(loop.details["operationalPolicies"]) > 0


@mock.patch.object(LoopInstance, 'send_message')
def test_update_microservice_policy(mock_send_message):
    """Test Loop Instance add TCA configuration."""
    loop = LoopInstance(template="template", name="LOOP_test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    loop.update_microservice_policy()
    mock_send_message.assert_called_once() 
    method, description, url , auth, key= mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD TCA config"
    assert url == (f"{loop.base_url}/loop/updateMicroservicePolicy/{loop.name}")
    assert auth == loop.pkcs12_filename
    assert key == loop.pkcs12_password
