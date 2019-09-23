# SPDX-License-Identifier: Apache-2.0

from onapsdk.utils.headers_creator import headers_sdc_creator
from onapsdk.utils.headers_creator import headers_aai_creator
from onapsdk.utils.headers_creator import headers_so_creator


def test_headers_sdc_creator():
    base_header = {}
    sdc_headers_creator = headers_sdc_creator(base_header)
    assert base_header != sdc_headers_creator
    assert sdc_headers_creator["USER_ID"] == "cs0008"
    assert sdc_headers_creator["Authorization"]

def test_headers_aai_creator():
    base_header = {}
    aai_headers_creator = headers_aai_creator(base_header)
    assert base_header != aai_headers_creator
    assert aai_headers_creator["x-fromappid"] == "AAI"
    assert aai_headers_creator["authorization"]
    assert aai_headers_creator["x-transactionid"]

def test_headers_so_creator():
    base_header = {}
    so_headers_creator = headers_so_creator(base_header)
    assert base_header != so_headers_creator
    assert so_headers_creator["x-fromappid"] == "AAI"
    assert so_headers_creator["authorization"]
    assert so_headers_creator["x-transactionid"]
