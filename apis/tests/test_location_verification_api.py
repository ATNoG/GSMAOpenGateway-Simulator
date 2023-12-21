# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-15 11:45:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-21 11:36:37

import pytest
import json
import config # noqa
from common.database import models
from fastapi.testclient import TestClient
from apis.main import device_location_verification_app
from datetime import datetime, timedelta
from common.apis.device_location_schemas import (
    VerificationResult
)

API_URL = "/location-verification/v0/verify"

client = TestClient(device_location_verification_app)


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
    'device_data_timestamp, desired_area, expected_verification_result, ' +
    'expected_verification_result_match_rate',
    [
        # Circles
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow(),
            {
                "areaType": "circle",
                "center": {
                    "latitude": 40.631221426476856,
                    "longitude": -8.656918534018967,
                },
                "radius": 58
            },
            VerificationResult.TRUE,
            None
        ),
        (
            40.63148536954102,
            -8.657291163208452,
            24,
            datetime.utcnow(),
            {
                "areaType": "circle",
                "center": {
                    "latitude": 40.631221426476856,
                    "longitude": -8.656918534018967,
                },
                "radius": 20
            },
            VerificationResult.PARTIAL,
            1
        ),
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow(),
            {
                "areaType": "circle",
                "center": {
                    "latitude": 40.631221426476856,
                    "longitude": -8.656918534018967,
                },
                "radius": 40
            },
            VerificationResult.PARTIAL,
            29
        ),
        (
            40.63148536954102,
            -8.657291163208452,
            20,
            datetime.utcnow(),
            {
                "areaType": "circle",
                "center": {
                    "latitude": 40.631221426476856,
                    "longitude": -8.656918534018967,
                },
                "radius": 20
            },
            VerificationResult.FALSE,
            None
        ),
        # Polygons
        (
            40.6344182,
            -8.657551,
            10,
            datetime.utcnow(),
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
            VerificationResult.FALSE,
            None
        ),
        (
            40.631649455486816,
            -8.657374926386364,
            10,
            datetime.utcnow(),
            {
                "areaType": "polygon",
                "boundary": [
                    {
                        "latitude": 40.63089367080003,
                        "longitude": -8.657870564576257
                    },
                    {
                        "latitude": 40.632901313175424,
                        "longitude": -8.660653736607372
                    },
                    {
                        "latitude": 40.635587146241264,
                        "longitude": -8.657286688802621
                    },
                    {
                        "latitude": 40.63297969815211,
                        "longitude": -8.654606590975272
                    }
                ]
            },
            VerificationResult.TRUE,
            None
        ),
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow(),
            {
                "areaType": "polygon",
                "boundary": [
                    {
                        "latitude": 40.63144894982574,
                        "longitude": -8.657921718780337
                    },
                    {
                        "latitude": 40.631110168126554,
                        "longitude": -8.657146608213026
                    },
                    {
                        "latitude": 40.63237597034829,
                        "longitude": -8.656390580233992
                    }
                ]
            },
            VerificationResult.TRUE,
            None
        ),
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow(),
            {
                "areaType": "polygon",
                "boundary": [
                    {
                        "latitude": 40.63144894982574,
                        "longitude": -8.657921718780337
                    },
                    {
                        "latitude": 40.631110168126554,
                        "longitude": -8.657146608213026
                    },
                    {
                        "latitude": 40.631515041275385,
                        "longitude": -8.657260959921645
                    },
                ]
            },
            VerificationResult.PARTIAL,
            48
        ),
        (
            40.63148536954102,
            -8.657291163208452,
            10,
            datetime.utcnow() - timedelta(seconds=10),
            {
                "areaType": "polygon",
                "boundary": [
                    {
                        "latitude": 40.63144894982574,
                        "longitude": -8.657921718780337
                    },
                    {
                        "latitude": 40.631110168126554,
                        "longitude": -8.657146608213026
                    },
                    {
                        "latitude": 40.630930013438984,
                        "longitude": -8.6580837866016
                    },
                ]
            },
            VerificationResult.FALSE,
            None
        ),
    ]
)
def test_ok_responses_in_verify_endpoint(
    device_latitude, device_longitude, device_radius, device_data_timestamp,
    desired_area,
    expected_verification_result, expected_verification_result_match_rate,
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
        data=json.dumps(
            {
                "device": {
                    "phoneNumber": "123456789",
                    "networkAccessIdentifier": "223456789@domain.com",
                    "ipv4Address": {
                        "publicAddress": "84.125.93.10",
                        "publicPort": 59765
                    },
                    "ipv6Address": "2001:db1:85a3:8d3:1319:8a2e:370:7344"
                },
                "area": desired_area,
                "maxAge": 60
            }
        )
    )

    response_data = response.json()
    print(f"Response Data: {response_data}")

    assert response.status_code == 200
    assert expected_verification_result.value == \
        response_data["verificationResult"]
    assert expected_verification_result_match_rate == \
        response_data["matchRate"]
    assert device_data_timestamp == datetime.strptime(
        response_data["lastLocationTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
    )


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
        data=json.dumps(
            {
                "device": {
                    "phoneNumber": "123456789",
                    "networkAccessIdentifier": "123456789@domain.com",
                    "ipv4Address": {
                        "publicAddress": "84.125.93.10",
                        "publicPort": 59765
                    },
                    "ipv6Address": "2001:db8:85a3:8d3:1319:8a2e:370:7344"
                },
                "area": desired_area,
                "maxAge": max_age
            }
        )
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
        data=json.dumps(
            {
                "device": {
                    "phoneNumber": "123456789",
                    "networkAccessIdentifier": "123456789@domain.com",
                    "ipv4Address": {
                        "publicAddress": "84.125.93.10",
                        "publicPort": 59765
                    },
                    "ipv6Address": "2001:db8:85a3:8d3:1319:8a2e:370:7344"
                },
                "area": desired_area,
                "maxAge": max_age
            }
        )
    )

    response_data = response.json()
    print(f"Response Data: {response_data}")

    assert response.status_code == 410
    assert response_data["status"] == 410
    assert response_data["code"] == 'SIMULATION.NOT_RUNNING'
    assert response_data["message"] == 'The simulation is not running. '\
        'Thus, you cannot get its generated data'
