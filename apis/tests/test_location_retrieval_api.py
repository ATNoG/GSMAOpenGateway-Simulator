# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-15 11:45:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-21 11:36:38

import pytest
import json
import config # noqa
from common.database import models
from fastapi.testclient import TestClient
from apis.main import device_location_retrieval_app
from datetime import datetime, timedelta

API_URL = "/location-retrieval/v0/retrieve"
REQUEST_DATA = {
    "device": {
        "phoneNumber": "123456789",
        "networkAccessIdentifier": "223456789@domain.com",
        "ipv4Address": {
            "publicAddress": "84.125.93.10",
            "publicPort": 59765
        },
        "ipv6Address": "2001:db1:85a3:8d3:1319:8a2e:370:7344"
    },
    "maxAge": 60
}

client = TestClient(device_location_retrieval_app)


def mocks_for_test_verify_endpoint(
    mocker, device_latitude, device_longitude, device_radius,
    device_data_timestamp
):

    # Assume that the simulation is running
    mocker.patch(
        target="common.database.crud.simulation_is_running",
        return_value=True
    )

    # Mock the Simulated UE Instance (in database)
    mocker.patch(
        target="common.database" +
        ".crud.get_simulated_device_instance_from_root_simulation",
        return_value=models.SimulationUEInstance(
            id=1,
            simulation_instance=0
        )
    )

    # Mock the UE radius
    mocker.patch(
        target="common.helpers.device_location.generate_random_radius",
        return_value=device_radius
    )

    # Mock the Simulated UE location data
    mocker.patch(
        target="common.database" +
        ".crud.get_device_location_simulation_data",
        return_value=models.DeviceLocationSimulationData(
            id=0,
            child_simulation_instance=0,
            simulation_instance=0,
            ue=1,
            latitude=device_latitude,
            longitude=device_longitude,
            timestamp=device_data_timestamp
        )
    )


@pytest.mark.parametrize(
    'device_latitude, device_longitude, device_radius, ' +
    'device_data_timestamp, expected_retrieval_area_type, ' +
    'expected_retrieval_center_latitude, ' +
    'expected_retrieval_center_longitude, expected_retrieval_radius',
    [
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow(),
            "circle",
            40.63148536954102,
            -8.657291163208452,
            10
        ),
        (
            40.63148536954220,
            -8.657291163208220,
            20,
            datetime.utcnow(),
            "circle",
            40.63148536954220,
            -8.657291163208220,
            20
        ),
    ]
)
def test_ok_responses_in_verify_endpoint(
    device_latitude, device_longitude, device_radius, device_data_timestamp,
    expected_retrieval_area_type, expected_retrieval_center_latitude,
    expected_retrieval_center_longitude, expected_retrieval_radius,
    mocker
):
    # Prepare the mocks
    mocks_for_test_verify_endpoint(
        mocker, device_latitude, device_longitude, device_radius,
        device_data_timestamp
    )

    response = client.post(
        url=API_URL,
        headers={"simulation-id": "1"},
        data=json.dumps(REQUEST_DATA)
    )

    response_data = response.json()
    print(f"Response Data: {response_data}")

    assert response.status_code == 200
    assert device_data_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ") == \
        response_data["lastLocationTime"]
    assert expected_retrieval_area_type == response_data["area"]["areaType"]
    assert expected_retrieval_center_latitude == response_data.get("area")\
        .get("center").get("latitude")
    assert expected_retrieval_center_longitude == response_data.get("area")\
        .get("center").get("longitude")
    assert expected_retrieval_radius == response_data.get("area").get("radius")


@pytest.mark.parametrize(
    'device_latitude, device_longitude, device_radius, ' +
    'device_data_timestamp, desired_area, max_age, ',
    [
        # Circles
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow() - timedelta(seconds=65),
            {
                "areaType": "circle",
                "center": {
                    "latitude": 40.631221426476856,
                    "longitude": -8.656918534018967,
                },
                "radius": 58
            },
            60
        ),
        # Polygons
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow() - timedelta(seconds=80),
            {
                "areaType": "polygon",
                "boundary": [
                    {
                        "latitude": 40.63202273604748,
                        "longitude": -8.657473571287921
                    },
                    {
                        "latitude": 40.6313957983325,
                        "longitude": -8.658503562294571,
                    },
                    {
                        "latitude": 40.63097238506017,
                        "longitude": -8.657537981681758
                    },
                    {
                        "latitude": 40.63132247705793,
                        "longitude": -8.656508000513412,
                    },
                ]
            },
            75
        ),
    ]
)
def test_bad_max_age_responses_in_verify_endpoint(
    device_latitude, device_longitude, device_radius, device_data_timestamp,
    desired_area, max_age, mocker
):
    # Prepare the mocks
    mocks_for_test_verify_endpoint(
        mocker, device_latitude, device_longitude, device_radius,
        device_data_timestamp
    )

    response = client.post(
        url=API_URL,
        headers={"simulation-id": "1"},
        data=json.dumps(REQUEST_DATA)
    )

    response_data = response.json()
    print(f"Response Data: {response_data}")

    assert response.status_code == 400
    assert response_data["status"] == 400
    assert response_data["code"] == \
        'LOCATION_RETRIEVAL.MAXAGE_INVALID_ARGUMENT'
    assert response_data["message"] == 'maxAge threshold cannot be satisfied'


@pytest.mark.parametrize(
    'desired_area, max_age',
    [
        (
            {
                "areaType": "circle",
                "center": {
                    "latitude": 40.631221426476856,
                    "longitude": -8.656918534018967,
                },
                "radius": 58
            },
            60
        )
    ]
)
def test_simulation_not_running_responses_in_verify_endpoint(
    desired_area, max_age, mocker
):
    # Prepare the mocks
    mocker.patch(
        target="common.database.crud.simulation_is_running",
        return_value=False
    )

    response = client.post(
        url=API_URL,
        headers={"simulation-id": "1"},
        data=json.dumps(REQUEST_DATA)
    )

    response_data = response.json()
    print(f"Response Data: {response_data}")

    assert response.status_code == 410
    assert response_data["status"] == 410
    assert response_data["code"] == 'SIMULATION.NOT_RUNNING'
    assert response_data["message"] == 'The simulation is not running. '\
        'Thus, you cannot get its generated data'
