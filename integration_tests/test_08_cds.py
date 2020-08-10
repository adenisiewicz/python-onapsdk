import pytest
import requests
import os

from tempfile import TemporaryDirectory, TemporaryFile

from onapsdk.configuration import settings

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

    # 0. test URLs
    response = requests.post("{}/api/v1/dictionary".format(CdsElement._url)) # TODO replace URL: settings.CDS_URL
    json_response = response.json()
    assert response.status_code == 200
    assert json_response['success'] == True
    assert json_response is not None

    response = requests.post("{}/api/v1/blueprint-model/enrich".format(CdsElement._url)) # TODO replace URL: settings.CDS_URL
    assert response.status_code == 200
    assert type(response.content) == bytes

    response = requests.post("{}/api/v1/blueprint-model/publish".format(CdsElement._url)) # TODO replace URL: settings.CDS_URL
    assert response.status_code == 200
    assert type(response.content) == bytes


    #  1. Read dd's from a file
    dd_set = DataDictionarySet.load_from_file(tmp_path_dd, False)

    #  2. Write dd's to the server
    dd_set.upload()

    #  3. Read Blueprint from  from a file
    blueprint = Blueprint.load_from_file(tmp_path_cba)
    assert type(blueprint.cba_file_bytes) == bytes

    #  4. Enrich and publish
    blueprint = blueprint.enrich()
    assert type(blueprint.cba_file_bytes) == bytes
    
    blueprint.publish()

    # #  5. Write enriched blueprint to a file
    with TemporaryDirectory() as tmpdirname:
        path = os.path.join(tmpdirname, "test-CBA-enriched.zip")
        blueprint.save(path)