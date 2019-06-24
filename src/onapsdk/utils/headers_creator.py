#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Header creator package."""
from typing import Dict

def headers_sdc_creator(base_header: Dict[str, str]):
    """
    Create the right headers for SDC creator type.

    Args:
        base_header (Dict[str, str]): the base header to use

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["USER_ID"] = "cs0008"
    headers["Authorization"] = ("Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2Uy"
                                "Z0F3ODR2YW9HR21KdlV5MlU=")
    return headers

def headers_aai_creator(base_header: Dict[str, str]):
    """
    Create the right headers for AAI creator type.

    Args:
        base_header (Dict[str, str]): the base header to use

    Returns:
        Dict[str, str]: the needed headers

    """
    headers = base_header.copy()
    headers["x-fromappid"] = "AAI"
    headers["x-transactionid"] = "0a3f6713-ba96-4971-a6f8-c2da85a3176e"
    headers["authorization"] = "Basic QUFJOkFBSQ=="
    return headers
