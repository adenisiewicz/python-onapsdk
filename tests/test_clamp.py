#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test vf module."""

from unittest import mock
from unittest.mock import MagicMock

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
    mock_send_message_json.assert_called_once_with('GET', 'Get Loop Templates', (f"{Clamp.base_url()}/templates/"))
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
            assert_called_once_with('GET', 'Get stocked policies', (f"{Clamp.base_url()}/policyToscaModels/"))
        assert exists 
