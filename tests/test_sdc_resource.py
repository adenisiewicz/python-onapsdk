#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcResource module."""
import mock
import pytest

import onapsdk.constants as const
from onapsdk.onap_service import OnapService
from onapsdk.sdc_resource import SdcResource
from onapsdk.vf import Vf
from onapsdk.vsp import Vsp
from onapsdk.constants import CERTIFIED, DRAFT, CHECKIN

def test_init():
    """Test the initialization."""
    element = SdcResource()
    assert isinstance(element, OnapService)

def test_class_variables():
    """Test the class variables."""
    assert SdcResource.server == "SDC"
    assert SdcResource.base_front_url == "https://sdc.api.fe.simpledemo.onap.org:30207"
    assert SdcResource.base_back_url == "https://sdc.api.be.simpledemo.onap.org:30204"
    assert SdcResource.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

@mock.patch.object(Vf, 'send_message_json')
def test__get_item_details_not_created(mock_send):
    vf = Vf()
    assert vf._get_item_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vsp, 'send_message_json')
def test__get_item_details_created(mock_send):
    vsp = Vsp()
    vsp.identifier = "1234"
    mock_send.return_value = {'return': 'value'}
    assert vsp._get_item_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item', "{}/items/1234/versions".format(vsp._base_url()))

@mock.patch.object(Vsp, 'send_message_json')
def test__get_items_version_details_not_created(mock_send):
    vsp = Vsp()
    assert vsp._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'load')
@mock.patch.object(Vf, 'send_message_json')
def test__get_items_version_details_no_version(mock_send, mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf._get_item_version_details() == {}
    mock_send.assert_not_called()

@mock.patch.object(Vf, 'send_message_json')
def test__get_items_version_details(mock_send):
    vf = Vf()
    vf.identifier = "1234"
    vf._version = "4567"
    mock_send.return_value = {'return': 'value'}
    assert vf._get_item_version_details() == {'return': 'value'}
    mock_send.assert_called_once_with('GET', 'get item version', "{}/items/1234/versions/4567".format(vf._base_url()))

@mock.patch.object(Vf, 'load')
def test__unique_uuid_no_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    vf._unique_uuid = "4567"
    assert vf.unique_uuid == "4567"
    mock_load.assert_not_called()

@mock.patch.object(Vf, 'load')
def test__unique_uuid_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf.unique_uuid == None
    mock_load.assert_called_once()

def test__unique_uuid_setter():
    vf = Vf()
    vf.identifier = "1234"
    vf.unique_uuid = "4567"
    assert vf._unique_uuid == "4567"

@mock.patch.object(Vf, 'deep_load')
def test__unique_identifier_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    assert vf.unique_identifier == None
    mock_load.assert_called_once()

@mock.patch.object(Vf, 'deep_load')
def test__unique_identifier_no_load(mock_load):
    vf = Vf()
    vf.identifier = "1234"
    vf._unique_identifier= "toto"
    assert vf.unique_identifier == "toto"
    mock_load.assert_not_called()

def test__status_setter():
    vf = Vf()
    vf.identifier = "1234"
    vf.status = "4567"
    assert vf._status == "4567"

@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_no_response(mock_send):
    vf = Vf()
    vf.identifier = "1234"
    vf._version = "4567"
    mock_send.return_value = {}
    vf.deep_load()
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf', "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url))

@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_OK(mock_send):
    vf = Vf()
    vf.identifier = "5689"
    vf._version = "4567"
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011'}]}
    vf.deep_load()
    assert vf.unique_identifier == "71011"
    mock_send.assert_called_once_with('GET', 'Deep Load Vf', "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url))

@mock.patch.object(Vf, 'send_message_json')
def test__deep_load_response_NOK(mock_send):
    vf = Vf()
    vf.identifier = "5678"
    vf._version = "4567"
    mock_send.return_value = {'resources': [{'uuid': '5689', 'name': 'test', 'uniqueId': '71011'}]}
    vf.deep_load()
    assert vf._unique_identifier is None
    mock_send.assert_called_once_with('GET', 'Deep Load Vf', "{}/sdc1/feProxy/rest/v1/followed".format(vf.base_front_url))

def test__parse_sdc_status_certified():
    assert SdcResource._parse_sdc_status("CERTIFIED") == CERTIFIED

def test__parse_sdc_status_draft():
    assert SdcResource._parse_sdc_status("NOT_CERTIFIED_CHECKOUT") == DRAFT

def test__parse_sdc_status_draft():
    assert SdcResource._parse_sdc_status("NOT_CERTIFIED_CHECKIN") == CHECKIN

def test__parse_sdc_status_unknown():
    assert SdcResource._parse_sdc_status("UNKNOWN") == 'UNKNOWN'

def test__parse_sdc_status_empty():
    assert SdcResource._parse_sdc_status("") is None

def test__really_submit():
    sdcResource = SdcResource()
    with pytest.raises(NotImplementedError):
        sdcResource._really_submit()
