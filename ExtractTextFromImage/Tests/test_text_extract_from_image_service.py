import json
import base64
import urllib
import urllib.parse
from urllib.request import Request
from urllib.error import URLError
import pytest

# Configuration settings TODO move some to config file.
sut_web_url = 'http://127.0.0.1:5000/'
image_path = 'image'
header_content_type_json = 'application/json'
headers = {'Content-Type': header_content_type_json}
image_base64_key = 'image-base64'

statement_image_file = "../ird-test-halifax-cc-statement.jpg"
with open(statement_image_file, 'rb') as document:
    image_bytes = bytearray(document.read())
image_base64 = base64.b64encode(image_bytes).decode()  # Encode image as b64 bytearray and decode into string


def test_api_when_get_root_url_then_return_404():
    try:
        with urllib.request.urlopen(sut_web_url) as response:
            http_resp = response.read()
            pytest.fail('Get and read succeeded: {}', http_resp.get_body())
    except urllib.error.HTTPError as e:
        assert e.code == 404


def test_api_when_get_false_path_then_return_404():
    try:
        with urllib.request.urlopen(sut_web_url+'false') as response:
            http_resp = response.read()
            pytest.fail('Get and read succeeded: {}', http_resp.get_body())
    except urllib.error.HTTPError as e:
        assert e.code == 404


def test_api_when_post_image_then_return_image_id():

    url = sut_web_url + image_path
    req_body = {image_base64_key: image_base64}  # dict containing string value
    json_body = json.dumps(req_body)        # string of JSON
    body = json_body.encode()        # bytearray

    req = urllib.request.Request(url, body, headers)

    with urllib.request.urlopen(req) as response:
        resp_json = response.read()
        resp_body = json.loads(resp_json)
        assert resp_body['image-id']
        assert len(resp_body['image-id']) != 0
        assert response.getcode() == 200
        assert response.info()['Content-Type'] == header_content_type_json


def test_api_when_post_image_then_get_image_return_valid_image_content():
    # Pre-condition - create image resource
    post_image_url = sut_web_url + image_path
    req_body = {image_base64_key: image_base64}  # dict
    json_body = json.dumps(req_body)  # string
    body = json_body.encode()  # bytearray

    post_req = urllib.request.Request(post_image_url, body, headers)

    with urllib.request.urlopen(post_req) as post_response:
        assert post_response.getcode() == 200
        assert post_response.info()['Content-Type'] == header_content_type_json

        post_image_resp_json = post_response.read()
        post_image_resp_body = json.loads(post_image_resp_json)
        assert post_image_resp_body['image-id']

    # Test & check post conditions
    with urllib.request.urlopen(post_image_url+'/'+post_image_resp_body['image-id']) as get_response:
        assert get_response.getcode() == 200
        assert 'Content-Type' in get_response.info()
        assert get_response.info()['Content-Type'] == header_content_type_json

        get_image_body_json = get_response.read()
        get_image_resp_dict = json.loads(get_image_body_json)
        assert 'image-base64' in get_image_resp_dict
        assert len(get_image_resp_dict['image-base64']) != 0
        assert get_image_resp_dict['image-base64'] == image_base64


def test_api_when_get_non_existant_object_then_return_not_found():
    post_image_url = sut_web_url + image_path
    try:
        urllib.request.urlopen(post_image_url+'/'+'false-image-key')
    except urllib.error.HTTPError as e:
        assert e.getcode() == 404
        # TODO check response body to check contents