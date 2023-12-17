# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 11:14:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-17 16:54:15

import utm
from schemas.device_location_schemas import (
    Location,
    Circle,
    Point,
    ErrorInfo,
    VerifyLocationResponse,
    VerificationResult
)
from datetime import datetime
from pyproj import Proj
from fastapi.responses import JSONResponse
import random
import config # noqa
from common.database import models
import hashlib
from shapely import geometry


def generate_random_radius(latitude, longitude):
    # Use hashlib to generate a hash from the input data
    hash_object = hashlib.md5(f"{latitude}{longitude}".encode())
    hash_digest = int(hash_object.hexdigest(), 16)

    # Set a seed for the random number generator based on the hash
    random.seed(hash_digest)

    # Generate a value from a normal distribution
    value = random.gauss(mu=10, sigma=5)

    # Ensure the generated value is always greater than 1
    return round(max(1, value), 2)


def create_location_message(
    device_location_data: models.DeviceLocationSimulationData
):
    return Location(
        last_location_time=device_location_data.timestamp.strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ'
        ),
        area=Circle(
            center=Point(
                latitude=device_location_data.latitude,
                longitude=device_location_data.longitude,
            ),
            radius=generate_random_radius(
                latitude=device_location_data.latitude,
                longitude=device_location_data.longitude
            )
        )
    )


def compute_simulated_data_age(
    device_location_data: models.DeviceLocationSimulationData
):
    # Get the current time
    current_time = datetime.now()

    # Compute the time difference
    time_difference = current_time - device_location_data.timestamp

    # Return the difference in seconds
    return time_difference.total_seconds()


def error_message_simulation_not_running():
    return JSONResponse(
            status_code=410,
            content=ErrorInfo(
                status=410,
                code="SIMULATION.NOT_RUNNING",
                message="The simulation is not running. Thus, you cannot " +
                "get its generated data"
            ).__dict__
        )


def error_message_max_age_exceeded():
    return JSONResponse(
            status_code=400,
            content=ErrorInfo(
                status=400,
                code="LOCATION_RETRIEVAL.MAXAGE_INVALID_ARGUMENT",
                message="maxAge threshold cannot be satisfied"
            ).__dict__
        )


# Geo Stuff
def get_utm_zone_from_coordinates(latitude: float, longitude: float) -> str:
    return utm.from_latlon(latitude, longitude)


def get_shapely_point_from_coordinates(latitude: float, longitude: float):
    # Get the UTM Zone
    _, _, zone_number, _ = get_utm_zone_from_coordinates(
        latitude=latitude,
        longitude=longitude
    )
    # Convert latitude and longitude to Cartesian coordinates
    project = Proj(proj='utm', zone=zone_number, ellps='WGS84')

    return project(longitude, latitude)


def shapely_circle_from_coordinates_circle(
    center_latitude, center_longitude, radius_meters
):
    center_x, center_y = get_shapely_point_from_coordinates(
        latitude=center_latitude,
        longitude=center_longitude
    )
    # Create a Point object for the circle center
    circle_center = geometry.Point(center_x, center_y)
    # Create a circle around the center with the specified radius
    circle = circle_center.buffer(radius_meters)
    return circle


def shapely_polygon_from_list_of_coordinates_points(coordinates_points):
    return geometry.Polygon(
        [
            get_shapely_point_from_coordinates(
                latitude=p.latitude,
                longitude=p.longitude
            )
            for p
            in coordinates_points
        ]
    )


def compute_location_verification_result(
    device: geometry.Polygon,
    area: geometry.Polygon
) -> VerifyLocationResponse:
    datetime_formatter = "%Y-%m-%dT%H:%M:%S.%fZ"
    # Verify if the device is fully contained in the area
    if area.contains(device):
        return VerifyLocationResponse(
            last_location_time=datetime.min.strftime(datetime_formatter),
            verification_result=VerificationResult.TRUE
        )

    # Verify if the device is partially contained in the area
    overlap = device.intersection(area)
    if overlap.area > 0:
        return VerifyLocationResponse(
            last_location_time=datetime.min.strftime(datetime_formatter),
            verification_result=VerificationResult.PARTIAL,
            matchRate=max(round(overlap.area/device.area*100), 1)
        )

    return VerifyLocationResponse(
        last_location_time=datetime.min.strftime(datetime_formatter),
        verification_result=VerificationResult.FALSE
    )