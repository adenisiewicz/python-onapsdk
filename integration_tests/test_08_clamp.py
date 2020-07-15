#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Integration test Clamp module."""
import os

import pytest

import requests

from onapsdk.service import Service
from onapsdk.clamp.clamp_element import Clamp
from onapsdk.clamp.loop_instance import LoopInstance

@pytest.mark.integration
def test_Clamp_requirements():
    """Integration tests for Clamp."""
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

@pytest.mark.integration
def test_Loop_creation():
    """Integration tests for Loop Instance."""
    requests.get("{}/reset".format(Clamp._base_url))
    Clamp.create_cert()
    svc = Service(name="service01")
    loop_template = Clamp.check_loop_template(service=svc)
    response = requests.post("{}/reset".format(Clamp._base_url))
    response.raise_for_status()
    loop = LoopInstance(template=loop_template, name="intance01", details={})
    details = loop.create()
    assert details

@pytest.mark.integration
def test_Loop_customization():
    """Integration tests for Loop Instance."""
    requests.get("{}/reset".format(Clamp._base_url))
    Clamp.create_cert()
    svc = Service(name="service01")
    loop_template = Clamp.check_loop_template(service=svc)
    response = requests.post("{}/reset".format(Clamp._base_url))
    response.raise_for_status()
    loop = LoopInstance(template=loop_template, name="intance01", details={})
    details = loop.create()
    assert details
    loop.update_microservice_policy()
    new_details = loop._update_loop_details()
    assert new_details
    #add op policy Guard that already exists
    added = loop.add_operational_policy(policy_type="onap.policies.controlloop.Guard",
                                        policy_version="1.0.0")
    assert added
