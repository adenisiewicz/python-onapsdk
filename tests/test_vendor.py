#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test vendor module."""
import mock
import pytest

from onapsdk.vendor import Vendor

@mock.patch.object(Vendor, 'send_message_json')
def test_get_all_no_vendors(mock_send):
    """Returns empty array if no vendors."""
    vendor = Vendor()
    mock_send.return_value = {}
    assert vendor.get_all() == []
    mock_send.assert_called_once_with("GET", 'get vendors', mock.ANY)

@mock.patch.object(Vendor, 'send_message_json')
def test_get_all_some_vendors(mock_send):
    """Returns a list of vendors."""
    vendor = Vendor()
    mock_send.return_value = {'results':[
        {'name': 'one', 'id': '1234'},
        {'name': 'two', 'id': '1235'}]}
    assert len(vendor.get_all()) == 2
    vendor_1 = vendor.get_all()[0]
    assert vendor_1.name == "one"
    assert vendor_1.identifier == "1234"
    assert vendor_1.created
    vendor_2 = vendor.get_all()[1]
    assert vendor_2.name == "two"
    assert vendor_2.identifier == "1235"
    assert vendor_2.created
    mock_send.assert_called_with("GET", 'get vendors', mock.ANY)

def test_init_no_name():
    """Check init with no names."""
    vendor = Vendor()
    assert vendor.identifier == None
    assert vendor.version == None
    assert vendor.name == "Generic-Vendor"
    assert vendor.created == False
    assert vendor.header["USER_ID"] == "cs0008"
    assert isinstance(vendor.base_url, str)
    assert "sdc1/feProxy/onboarding-api/v1.0" in vendor.base_url

def test_init_with_name():
    """Check init with no names."""
    vendor = Vendor(name="YOLO")
    assert vendor.identifier == None
    assert vendor.version == None
    assert vendor.name == "YOLO"
    assert vendor.created == False
    assert vendor.header["USER_ID"] == "cs0008"
    assert isinstance(vendor.base_url, str)
    assert "sdc1/feProxy/onboarding-api/v1.0" in vendor.base_url

def test_equality_really_equals():
    """Check two Vendors are equals if name is the same."""
    vendor_1 = Vendor(name="equal")
    vendor_1.identifier  = "1234"
    vendor_2 = Vendor(name="equal")
    vendor_2.identifier  = "1235"
    assert vendor_1 == vendor_2

def test_equality_not_equals():
    """Check two Vendors are not equals if name is not the same."""
    vendor_1 = Vendor(name="equal")
    vendor_1.identifier  = "1234"
    vendor_2 = Vendor(name="not_equal")
    vendor_2.identifier  = "1234"
    assert vendor_1 != vendor_2


def test_equality_not_equals_not_same_object():
    """Check a Vendor and something different are not equals."""
    vendor_1 = Vendor(name="equal")
    vendor_1.identifier  = "1234"
    vendor_2 = "equal"
    assert vendor_1 != vendor_2

@mock.patch.object(Vendor, 'get_all')
def test_exists_not_exists(mock_get_all):
    """Return False if vendor doesn't exist in SDC."""
    vendor_1 = Vendor(name="one")
    vendor_1.identifier = "1234"
    vendor_1.created = True
    mock_get_all.return_value = [vendor_1]
    vendor = Vendor(name="two")
    assert not vendor.exists()

@mock.patch.object(Vendor, 'get_all')
@mock.patch.object(Vendor, 'send_message_json')
def test_exists_exists(mock_send, mock_get_all):
    """Return True if vendor exists in SDC."""
    vendor_1 = Vendor(name="one")
    vendor_1.identifier = "1234"
    vendor_1.created = True
    mock_get_all.return_value = [vendor_1]
    mock_send.return_value = {'results':
        [{'status': 'state_one', 'id': "5678"}]}
    vendor = Vendor(name="one")
    assert vendor.exists()
    assert vendor.status == "state_one"
    assert vendor.version == "5678"
