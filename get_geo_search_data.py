import requests


def get_geo_data(q):
    url = 'https://admin.barikoi.xyz:8090/v2/search/autocomplete/web?q=' + q
    try:
        return requests.get(url).json()['places']
    except Exception as e:
        print(e)
        return []


if __name__ == "__main__":
    print(get_geo_data('mirpur'))
