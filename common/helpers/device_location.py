# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 11:14:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 21:07:45

import utm
from datetime import datetime
from pyproj import Proj
from fastapi.responses import JSONResponse
import random
import config # noqa
from common.apis import simulation_schemas as SimulationSchemas
from common.apis.device_location_schemas import (
    Location,
    Circle,
    Point,
    ErrorInfo,
    VerifyLocationResponse,
    VerificationResult,
    Device,
    DeviceIpv4Addr,
    Area,
    Polygon,
    Webhook,
    SubscriptionInfo,
    SubscriptionDetail
)
from common.database import models
import hashlib
from shapely import geometry
import json


def parse_payload_ues_to_simulated_ue_objects(payload_devices):

    simulated_devices = []

    for device in payload_devices:
        # Start by casting the entire object
        simulated_device = SimulationSchemas.SimulationUE(**device)

        # Check for extra attributes that might not have been parsed
        if "ipv4_address" in device:
            simulated_device.ipv4_address.private_address = \
                device["ipv4_address"].get("private_address")
            simulated_device.ipv4_address.public_port = \
                device["ipv4_address"].get("public_port")
            simulated_device.ipv4_address.public_address = \
                device["ipv4_address"].get("public_address")

        simulated_devices.append(simulated_device)

    return simulated_devices


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
    current_time = datetime.utcnow()

    # Compute the time difference
    time_difference = current_time - device_location_data.timestamp

    # Return the difference in seconds
    return time_difference.total_seconds()


def error_message_simulation_not_running():
    return JSONResponse(
            status_code=404,
            content=ErrorInfo(
                status=404,
                code="SIMULATION.NOT_RUNNING",
                message="The simulation is not running. Thus, you cannot " +
                "get its generated data"
            ).__dict__
        )


def subscription_not_found():
    return JSONResponse(
            status_code=404,
            content=ErrorInfo(
                status=404,
                code="NOT_FOUND",
                message="The specified resource is not found"
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


def shapely_circle_from_coordinates_circle_without_radius(
    center_latitude, center_longitude
):
    # Get a random radius
    radius = generate_random_radius(center_latitude, center_longitude)
    # Return built circle
    return shapely_circle_from_coordinates_circle(
        center_latitude=center_latitude,
        center_longitude=center_longitude,
        radius_meters=radius
    )


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


def shapely_polygon_from_area(area):
    # Filter according to the area type
    if area.area_type == "circle":
        return shapely_circle_from_coordinates_circle(
            center_latitude=area.center.latitude,
            center_longitude=area.center.longitude,
            radius_meters=area.radius
        )
    # else -> its a polygon
    else:
        return shapely_polygon_from_list_of_coordinates_points(
            coordinates_points=area.boundary
        )


def parse_simulation_ue_to_pydantic_device(
    simulation_ue: models.SimulationUE
) -> Device:
    ipv4_address = DeviceIpv4Addr()

    if simulation_ue.ipv4_address_public_address:
        ipv4_address.public_address = simulation_ue\
            .ipv4_address_public_address
    if simulation_ue.ipv4_address_private_address:
        ipv4_address.private_address = simulation_ue\
            .ipv4_address_private_address
    if simulation_ue.ipv4_address_public_port:
        ipv4_address.public_port = simulation_ue\
            .ipv4_address_public_port

    return Device(
        phone_number=simulation_ue.phone_number,
        network_access_identifier=simulation_ue.network_access_identifier,
        ipv4_address=ipv4_address,
        ipv6_address=simulation_ue.ipv6_address,
    )


def parse_area_dict_to_pydantic_area(
    area_dict
) -> Area:
    return Circle(**area_dict) if area_dict["area_type"] == "circle" \
        else Polygon(**area_dict)


def pydantic_subscription_info_from_db_subscription(
    db_subscription, simulated_device_from_db
):
    # Recreate the Webhook Object
    webook = Webhook(
        notificationUrl=db_subscription.webhook_url,
        notificationAuthToken=db_subscription.webhook_auth_token
    )

    device = parse_simulation_ue_to_pydantic_device(
        simulated_device_from_db
    )

    subscription_detail = SubscriptionDetail(
        device=device,
        area=parse_area_dict_to_pydantic_area(
            json.loads(json.loads(db_subscription.area))
        ),
        type=db_subscription.subscription_type
    )

    return SubscriptionInfo(
        webhook=webook,
        subscription_detail=subscription_detail,
        subscription_expire_time=db_subscription.expire_time,
        subscription_id=db_subscription.id,
        starts_at=db_subscription.start_time,
        expires_at=db_subscription.expire_time
    )
