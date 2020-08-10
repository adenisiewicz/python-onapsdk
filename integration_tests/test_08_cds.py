import pytest
import requests

from onapsdk.cds.blueprint import Blueprint, CbaMetadata, Mapping, MappingSet, Workflow
from onapsdk.cds.cds_element import CdsElement
from onapsdk.cds.data_dictionary import DataDictionary, DataDictionarySet



@pytest.mark.integration
def test_CDS_request():
    """Integration tests for CDS. """

    # TODO
    #  1. Read dd's from a file
    #  2. Write dd's to the server
    #  3. Read Blueprint from from a file
    #  4. Enrich and publish
    #  5. Write enriched blueprint to a file

    # 0. define paths
    # TODO move links or substitute with tempfiles
    CdsElement._url = "http://127.0.0.1:8080"
    tmp_path_dd = "C:\\Users\\IHalych\\Desktop\\Projects\\files\\dd.json"
    tmp_path_cba = "C:\\Users\\IHalych\\Desktop\\Projects\\files\\vLB_CBA_Python.zip"
    save_blueprint_file = "C:\\Users\\IHalych\\Desktop\\Projects\\files\\saved_cba\\tmp_vLB_CBA_Python.zip"

    # 0. test URLs
    response = requests.post("{}/api/v1/dictionary".format(CdsElement._url))
    json_response = response.json()
    assert response.status_code == 200
    assert json_response['success'] == True
    assert json_response is not None

    response = requests.post("{}/api/v1/blueprint-model/enrich".format(CdsElement._url))
    assert response.status_code == 200
    assert type(response.content) == bytes

    response = requests.post("{}/api/v1/blueprint-model/publish".format(CdsElement._url))
    assert response.status_code == 200
    assert type(response.content) == bytes


    #  1. Read dd's from a file
    dd_set = DataDictionarySet.load_from_file(tmp_path_dd, False)

    #  2. Write dd's to the server
    dd_set.upload()
    # TODO test result

    #  3. Read Blueprint from  from a file
    blueprint = Blueprint.load_from_file(tmp_path_cba)
    # TODO test result

    #  4. Enrich and publish
    blueprint = blueprint.enrich()
    assert blueprint.cba_file_bytes is not None
    assert type(blueprint.cba_file_bytes) == bytes
    
    blueprint.publish()
    # TODO test result
    # TODO add response?

    # #  5. Write enriched blueprint to a file
    blueprint.save(save_blueprint_file)
    # TODO test result