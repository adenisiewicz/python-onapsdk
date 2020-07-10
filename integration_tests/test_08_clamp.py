#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Clamp module."""
import os

import pytest

import requests

from onapsdk.service import Service
from onapsdk.clamp.clamp_element import Clamp


@pytest.mark.integration
def test_Clmap_requirements():
    requests.get("{}/reset".format(Clamp._base_url))
    Clamp.create_cert()
    #no add resource in clamp
    #svc.name already exists in mock clamp
    svc = Service(name="service01")
    template_exists = Clamp.check_loop_template(service=svc)
    assert template_exists
    policy_exists = Clamp.check_policies(policy_name="MinMax",
                                         req_policies=2)
    assert policy_exists
