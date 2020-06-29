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
    "components" : {
        "POLICY" : {
            "componentState" : {
                "stateName" : "UNKNOWN"
            }
        },
        "DCAE" : {
            "componentState" : {
                "stateName" : "BLUEPRINT_DEPLOYED"
            }
        }
    },
    "modelService" : {
        "resourceDetails": {
            "VFModule" : {
                "resourcecID" : {
                    "vfModuleModelName" : "resourcecID",
                    "vfModuleModelInvariantUUID" : "InvariantUUID",
                    "vfModuleModelUUID" : "UUID",
                    "vfModuleModelVersion" : "1.0",
                    "vfModuleModelCustomizationUUID" : "CustomizationUUID"
                }
            }
        }
    },
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
                                                   (f"{Clamp.base_url()}/templates/"))
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
                                    (f"{Clamp.base_url()}/policyToscaModels/"))
        assert exists 


def test_cl_initialization():
    """Class initialization test."""
    loop = LoopInstance(template="template", name="LOOP_name", details={})
    assert isinstance(loop, LoopInstance)


@mock.patch.object(LoopInstance, 'send_message_json')
def test_update_loop_details(mock_send_message_json):
    """Test Loop instance methode."""
    loop = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = LOOP_DETAILS
    loop.details = loop.update_loop_details()
    mock_send_message_json.assert_called_once_with('GET', 'Get loop details',
         (f"{loop.base_url}/loop/test"))
    assert loop.details == LOOP_DETAILS


@mock.patch.object(LoopInstance, 'send_message_json')
def test_create(mock_send_message_json):
    """Test Loop instance creation."""
    instance = LoopInstance(template="template", name="test", details={})
    mock_send_message_json.return_value = LOOP_DETAILS
    instance.create()
    mock_send_message_json.assert_called_once_with('POST', 'Create Loop Instance',
         (f"{instance.base_url}/loop/create/test?templateName=template"))
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
        (f"{loop.base_url}/loop/addOperationaPolicy/{loop.name}/policyModel/FrequencyLimiter/1.0.0"))
    assert loop.name == "LOOP_test"
    assert len(loop.details["operationalPolicies"]) > 0


@mock.patch.object(LoopInstance, 'send_message')
def test_update_microservice_policy(mock_send_message):
    """Test Loop Instance add TCA configuration."""
    loop = LoopInstance(template="template", name="LOOP_test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    loop.update_microservice_policy()
    mock_send_message.assert_called_once() 
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD TCA config"
    assert url == (f"{loop.base_url}/loop/updateMicroservicePolicy/{loop.name}")


@mock.patch.object(LoopInstance, 'send_message')
def test_add_drools_conf(mock_send_message):
    """Test Loop Instance add drools configuration."""
    loop = LoopInstance(template="template", name="LOOP_test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    entity_ids = loop.add_drools_conf()
    mock_send_message.assert_called_once() 
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD drools config"
    assert url == (f"{loop.base_url}/loop/updateOperationalPolicies/{loop.name}")
    assert entity_ids["resourceID"] == "resourcecID"


@mock.patch.object(LoopInstance, 'send_message')
def test_add_frequency_limiter(mock_send_message):
    """Test Loop Instance add frequency configuration."""
    loop = LoopInstance(template="template", name="LOOP_test", details=LOOP_DETAILS)
    mock_send_message.return_value = True
    loop.add_frequency_limiter()
    #add with the default frequency 1 
    mock_send_message.assert_called_once() 
    method, description, url = mock_send_message.call_args[0]
    assert method == "POST"
    assert description == "ADD frequency limiter config"
    assert url == (f"{loop.base_url}/loop/updateOperationalPolicies/{loop.name}")


SUBMITED_POLICY = {
        "components" : {
        "POLICY" : {
            "componentState" : {
                "stateName" : "SENT_AND_DEPLOYED"
            }
        }
    }
}

NOT_SUBMITED_POLICY = {
        "components" : {
        "POLICY" : {
            "componentState" : {
                "stateName" : "SENT"
            }
        }
    }
}


@mock.patch.object(LoopInstance, 'update_loop_details')
@mock.patch.object(LoopInstance, 'send_message_json')
def test_submit_policy(mock_send_message_json, mock_update):
    """Test submit policies to policy engine."""
    loop = LoopInstance(template="template", name="LOOP_test", details=LOOP_DETAILS)
    mock_send_message_json.return_value = True
    mock_update.return_value = SUBMITED_POLICY
    action = loop.act_on_loop_policy("submit")
    mock_send_message_json.assert_called_once_with('PUT',
                                                   'submit policy',
                                                   (f"{loop.base_url}/loop/submit/LOOP_test"))
    mock_update.assert_called_once()
    assert loop.details["components"]["POLICY"]["componentState"]["stateName"] == "SENT_AND_DEPLOYED"
    assert action


@mock.patch.object(LoopInstance, 'update_loop_details')
@mock.patch.object(LoopInstance, 'send_message_json')
def test_not_submited_policy(mock_send_message_json, mock_update):
    """Test submit policies to policy engine."""
    loop = LoopInstance(template="template", name="LOOP_test", details=LOOP_DETAILS)
    mock_send_message_json.return_value = True
    mock_update.return_value = NOT_SUBMITED_POLICY
    action = loop.act_on_loop_policy("submit")
    mock_send_message_json.assert_called_once_with('PUT',
                                                   'submit policy',
                                                   (f"{loop.base_url}/loop/submit/LOOP_test"))
    mock_update.assert_called_once()
    assert loop.details["components"]["POLICY"]["componentState"]["stateName"] == "SENT"
    assert not action


SUBMITED = {
        "components" : {
        "DCAE" : {
            "componentState" : {
                "stateName" : "MICROSERVICE_INSTALLED_SUCCESSFULLY"
            }
        }
    }
}

NOT_SUBMITED = {
        "components" : {
        "DCAE" : {
            "componentState" : {
                "stateName" : "MICROSERVICE_INSTALLATION_FAILED"
            }
        }
    }
}


@mock.patch.object(LoopInstance, 'update_loop_details')
@mock.patch.object(LoopInstance, 'send_message_json')
def test_not_submited_microservice_to_dcae(mock_send_message_json, mock_update):
    """Test deploy microservice to DCAE."""
    loop = LoopInstance(template="template", name="LOOP_test", details=LOOP_DETAILS)
    mock_send_message_json.return_value = True
    mock_update.return_value = SUBMITED
    deploy = loop.deploy_microservice_to_dcae()
    mock_send_message_json.assert_called_once_with('PUT',
                                                   'Deploy microservice to DCAE',
                                                   (f"{loop.base_url}/loop/deploy/LOOP_test"))
    assert loop.details["components"]["DCAE"]["componentState"]["stateName"] == "MICROSERVICE_INSTALLED_SUCCESSFULLY"
    assert deploy == True
