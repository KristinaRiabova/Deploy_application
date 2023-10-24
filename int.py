import pytest
import requests
from datetime import datetime, timedelta

from main import app, user_data_storage


BASE_URL = 'http://127.0.0.1:5000'


def send_request(url, method='GET', data=None):
    if method == 'GET':
        response = requests.get(f'{BASE_URL}{url}')
    elif method == 'POST':
        response = requests.post(f'{BASE_URL}{url}', json=data)
    return response



@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_user_intervals(client):
    response = send_request('/user_intervals')
    assert response.status_code == 200


def test_get_total_user_online_time(client):
    response = send_request('/api/stats/user/total?userId=example_user_id')
    assert response.status_code == 200




def test_forget_user_data(client):
    response = send_request('/api/user/forget?userId=example_user_id', method='POST')
    assert response.status_code == 200


def test_create_report(client):
    data = {
        'report_name': 'example_report',
        'metrics': ['dailyAverage', 'total'],
        'users': ['02d4563d-5727-c811-b3b7-57a10f6be25a', '05227367-07f0-b3a5-8345-2513e0c45cca'],

    }
    response = send_request('/api/report/test_report', method='POST', data=data)
    assert response.status_code == 200

def test_get_report(client):
    response = send_request('/api/report/test_report?from=2023-10-01T00:00&to=2023-10-21T:59')
    assert response.status_code == 500



def test_get_report_not_found(client):

    response = send_request('/api/report/nonexistent_report?from=2023-10-01T00:00&to=2023-10-21T23:59')
    assert response.status_code == 404

def test_get_report_missing_parameters(client):

    response = send_request('/api/report/test_report')
    assert response.status_code == 400


def test_get_report_with_global_metrics(client):

    data = {
        'report_name': 'example_report',
        'metrics': ['dailyAverage', 'total'],
        'users': ['02d4563d-5727-c811-b3b7-57a10f6be25a', '05227367-07f0-b3a5-8345-2513e0c45cca'],
    }
    send_request('/api/report/test_report', method='POST', data=data)


    user_metrics_1 = {
        "dailyAverage": 1500,
        "total": 36000,
    }
    user_metrics_2 = {
        "dailyAverage": 1400,
        "total": 33600,
    }


    user_data_storage['02d4563d-5727-c811-b3b7-57a10f6be25a'] = [user_metrics_1]
    user_data_storage['05227367-07f0-b3a5-8345-2513e0c45cca'] = [user_metrics_2]

    from_date = '2023-10-01T00'
    to_date = '2023-10-21T23:59'


    response = send_request(f'/api/report/test_report?from={from_date}&to={to_date}')

    assert response.status_code == 500




if __name__ == '__main__':
    pytest.main()
