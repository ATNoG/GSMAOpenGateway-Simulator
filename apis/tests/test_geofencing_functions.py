# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-15 11:45:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-19 18:38:17

import config # noqa
import pytest
from common.helpers import (
    device_location as DeviceLocationHelper
)
from common.apis.device_location_schemas import (
    VerificationResult
)



@pytest.mark.parametrize(
    'lat, long, expected_zone_number, expected_zone_letter',
    [
        # Aveiro, Portugal
        (
            40.630331280660066,
            -8.656657389168178,
            29,
            'T'
        ),
        # New York, USA
        (
            40.712775,
            -74.005973,
            18,
            'T'
        ),
        # Tokyo, Japan
        (
            35.689487,
            139.691706,
            54,
            'S'
        ),
    ]
)
def test_get_utm_zone_from_coordinates(
    lat, long, expected_zone_number, expected_zone_letter
):
    _, _, zone_number, zone_letter = DeviceLocationHelper\
        .get_utm_zone_from_coordinates(
            latitude=lat,
            longitude=long
        )
    assert zone_number == expected_zone_number
    assert zone_letter == expected_zone_letter


@pytest.mark.parametrize(
    'device, area, expected_verification_result, expected_match_rate',
    [
        (
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.63148536954102,
                center_longitude=-8.657291163208452,
                radius_meters=20
            ),
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.631221426476856,
                center_longitude=-8.656918534018967,
                radius_meters=20
            ),
            VerificationResult.FALSE,
            None
        ),
        (
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.63148536954102,
                center_longitude=-8.657291163208452,
                radius_meters=24
            ),
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.631221426476856,
                center_longitude=-8.656918534018967,
                radius_meters=20
            ),
            VerificationResult.PARTIAL,
            1
        ),
        (
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.63148536954102,
                center_longitude=-8.657291163208452,
                radius_meters=10
            ),
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.631221426476856,
                center_longitude=-8.656918534018967,
                radius_meters=40
            ),
            VerificationResult.PARTIAL,
            29
        ),
        (
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.63148536954102,
                center_longitude=-8.657291163208452,
                radius_meters=10
            ),
            DeviceLocationHelper.shapely_circle_from_coordinates_circle(
                center_latitude=40.631221426476856,
                center_longitude=-8.656918534018967,
                radius_meters=58
            ),
            VerificationResult.TRUE,
            None
        ),
    ]
)
def test_compute_location_verification_result(
    device, area, expected_verification_result, expected_match_rate
):
    result = DeviceLocationHelper.compute_location_verification_result(
        device=device,
        area=area
    )
    assert result.verification_result == expected_verification_result
    assert result.match_rate == expected_match_rate
