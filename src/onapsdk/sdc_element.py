#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""SDC Element module."""
from typing import Dict

from onapsdk.onap_service import OnapService

class SdcElement(OnapService):
    """Mother Class of all SDC elements."""

    def __init__(self):
        """Initialize SDC element."""
        super().__init__()
        self.server: str = "SDC"
        self.header: Dict[str, str] = self.__header()
        self.base_front_url = "http://sdc.api.fe.simpledemo.onap.org:30206"
        self.base_back_url = "http://sdc.api.be.simpledemo.onap.org:30205"

    @staticmethod
    def __header() -> Dict[str, str]:
        """
        Generate SDC header.

        Returns:
            The header dictionnary for SDC

        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "USER_ID": "sdc_user_id",
            "Authorization":
                "Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU=",
            "cache-control": "no-cache"
        }
