from collections.abc import Iterable
from unittest import mock


import pytest

from onapsdk.sdnc.preload import PreloadInformation, VfModulePreload


PRELOAD_INFORMATIONS = {
    'preload-information': {
        'preload-list': [
            {
                'preload-id': 'Python_ONAP_SDK_network_instance_338d5238-22fe-44d1-857a-223e2f6edd9b', 
                'preload-type': 'network', 
                'preload-data': {
                    'preload-network-topology-information': {
                        'physical-network-name': 'Not Aplicable', 
                        'is-provider-network': False, 
                        'is-external-network': False, 
                        'network-topology-identifier-structure': {
                            'network-technology': 'neutron', 
                            'network-type': 'Generic NeutronNet', 
                            'network-name': 'Python_ONAP_SDK_network_instance_338d5238-22fe-44d1-857a-223e2f6edd9b', 
                            'network-role': 'integration_test_net'
                        }, 
                        'is-shared-network': False
                    }, 
                    'preload-oper-status': {
                        'create-timestamp': '2020-06-26T09:12:03.708Z', 
                        'order-status': 'PendingAssignment'
                    }
                }
            }, 
            {
                'preload-id': 'Python_ONAP_SDK_network_instance_5d61bcf6-ec37-4cea-9d1b-744d0c2b75b9', 
                'preload-type': 'network', 
                'preload-data': {
                    'preload-network-topology-information': {
                        'is-provider-network': False, 
                        'is-external-network': False, 
                        'network-topology-identifier-structure': {
                            'network-technology': 'neutron', 
                            'network-type': 'Generic NeutronNet', 
                            'network-name': 'Python_ONAP_SDK_network_instance_5d61bcf6-ec37-4cea-9d1b-744d0c2b75b9', 
                            'network-id': '1234', 
                            'network-role': 'integration_test_net'
                        }, 
                        'is-shared-network': False
                    }, 
                    'preload-oper-status': {
                        'create-timestamp': '2020-06-25T12:22:35.939Z', 
                        'order-status': 'PendingAssignment'
                    }
                }
            }
        ]
    }
}


@mock.patch.object(VfModulePreload, "send_message_json")
def test_vf_module_preload_gr_api(mock_send_message_json):
    VfModulePreload.upload_vf_module_preload(vnf_instance=mock.MagicMock(),
                                             vf_module_instance_name="test",
                                             vf_module=mock.MagicMock())
    mock_send_message_json.assert_called_once()
    method, description, url = mock_send_message_json.call_args[0]
    assert method == "POST"
    assert description == "Upload VF module preload using GENERIC-RESOURCE-API"
    assert url == (f"{VfModulePreload.base_url}/restconf/operations/"
                   "GENERIC-RESOURCE-API:preload-vf-module-topology-operation")


@mock.patch.object(PreloadInformation, "send_message_json")
def test_preload_information(mock_send_message_json):
    mock_send_message_json.return_value = PRELOAD_INFORMATIONS
    preload_informations = PreloadInformation.get_all()
    assert isinstance(preload_informations, Iterable)
    preload_informations_list = list(preload_informations)
    assert len(preload_informations_list) == 2
    preload_information = preload_informations_list[0]
    assert isinstance(preload_information, PreloadInformation)
    assert preload_information.preload_id == "Python_ONAP_SDK_network_instance_338d5238-22fe-44d1-857a-223e2f6edd9b"
    assert preload_information.preload_type == "network"
