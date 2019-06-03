#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Test SdcElement module."""
import pytest

from onapsdk.sdc_element import SdcElement

def test_init():
    """Test the initialization."""
    element = SdcElement()
    assert element.server == "SDC"
    assert element.base_front_url == "http://sdc.api.fe.simpledemo.onap.org:30206"
    assert element.base_back_url == "http://sdc.api.be.simpledemo.onap.org:30205"
    assert element.header == {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "USER_ID": "sdc_user_id",
            "Authorization":
                "Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=",
            "cache-control": "no-cache"
        }
