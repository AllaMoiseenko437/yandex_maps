import pytest
import requests

@pytest.fixture
def yandex_api_key():
    return "135e7b2a-92bc-4c5a-9dda-e2b338d43fda"

@pytest.fixture
def yandex_search_api_key():
    return "35d69bd7-9119-4f5d-a5b6-f61fe3e09196"

@pytest.fixture
def geocode_base_url():
    return 'https://geocode-maps.yandex.ru/1.x/'

@pytest.fixture
def search_base_url():
    return 'https://search-maps.yandex.ru/v1/'

@pytest.mark.parametrize("address", [
    'Минск',
    'Минск, Шатько',
    'Минск, Шатько, дом 22',
    'Минск, -, дом -22'
])
def test_geocoding(geocode_base_url, yandex_api_key, address):
    params = {
        'apikey': yandex_api_key,
        'geocode': address,
        'format': 'json'
    }

    location = requests.get(geocode_base_url, params=params)

    print("Получаем местоположение: " + location.text)
    assert location.status_code == 200
    print(location.headers)
    assert location.headers['Content-Type'] == 'application/json; charset=utf-8'
    json_response = location.json()
    assert 'GeoObjectCollection' in json_response['response'], "Ответ не содержит ключ 'GeoObjectCollection'"


@pytest.mark.parametrize("text, ll, results", [
    ('кафе', '30.332934,53.899304', '5'),
    ('кафе', '30.350148,53.88150', '16'),
    ('магазин', '30.350148,53.88150', 'А'),
    ('парк', '30.350148,53.88150', '-2')
])
def test_search_cafe(search_base_url, yandex_search_api_key, text, ll, results):
    params = {
        'apikey': yandex_search_api_key,
        'text': text,
        'lang': 'ru_RU',
        'll': ll,
        'type': 'biz',
        'results': results
    }

    search_biz = requests.get(search_base_url, params=params)

    print(f"Кафе: {search_biz.text}")
    assert search_biz.status_code == 200
    assert search_biz.headers['Content-Type'] == 'application/json; charset=utf-8'
    json_response = search_biz.json()
    assert 'features' in json_response, "Ответ не содержит ключ 'features'"


def test_geocode(geocode_base_url, yandex_api_key):
    uri = 'ymapsbm1://org?oid=194084569841'

    params = {
        'apikey': yandex_api_key,
        'uri': uri,
        'format': 'json'
    }

    search_cafe = requests.get(geocode_base_url, params=params)

    print(f"Ответ геокодирования: {search_cafe.text}")
    assert search_cafe.status_code == 200
    assert search_cafe.headers['Content-Type'] == 'application/json; charset=utf-8'
    json_response = search_cafe.json()

    feature_member = json_response['response']['GeoObjectCollection']['featureMember']

    address_found = any(
        "Сел и съел" in feature['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
        for feature in feature_member
    )
    assert address_found, "Ожидаемый адрес 'Сел и съел' не найден в GeoObject"


def test_geocode_invalid_uri(geocode_base_url, yandex_api_key):
    uri = 'ym456bm1://org?oid=19408rty9841'

    params = {
        'apikey': yandex_api_key,
        'uri': uri,
        'format': 'json'
    }

    error = requests.get(geocode_base_url, params=params)

    print(f"Ответ при неверном URI: {error.text}")
    assert error.status_code == 400
    assert error.headers['Content-Type'] == 'application/json; charset=utf-8'
    json_response = error.json()