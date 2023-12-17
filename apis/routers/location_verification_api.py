# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 14:15:29
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-17 16:55:26
# coding: utf-8
from fastapi import APIRouter, Body, Header, Depends
from schemas.device_location_schemas import (
    VerifyLocationRequest
)
import config # noqa
from sqlalchemy.orm import Session
import logging
from helpers import device_location as DeviceLocationHelper
from helpers.responses_documentation.location_verification_api import (
    LocationVerificationResponses
)
from common.database import connections_factory as DBFactory
from common.database import crud

router = APIRouter()


@router.post(
    "/verify",
    responses=LocationVerificationResponses.POST_VERIFY,
    tags=["Location verification"],
    summary="Execute location verification for a user equipment",
    response_model_by_alias=True,
)
async def verify_location(
    simulation_id: int = Header(),
    verify_location_request: VerifyLocationRequest = Body(),
    db: Session = Depends(DBFactory.get_db_session)
):
    # We can only retrieve locations if the simulation is active
    if not crud.simulation_is_running(db=db, simulation_id=simulation_id):
        logging.info(
            "Impossible to retrieve locations for Simulation " +
            f"{simulation_id}. This Simulation is not running. It must be " +
            "started first."
        )
        return DeviceLocationHelper.error_message_simulation_not_running()

    # Get the Simulated UE ID
    simulated_ue = crud.get_simulated_device_from_root_simulation(
        db=db,
        root_simulation_id=simulation_id,
        device=verify_location_request.device
    )

    # Obtain the simulate data regarding that Simulated UE
    device_location_data = crud.get_device_location_simulation_data(
        db=db,
        root_simulation_id=simulation_id,
        ue=simulated_ue
    )

    # Get the simulated data age (seconds)
    simulated_data_age = DeviceLocationHelper.compute_simulated_data_age(
        device_location_data=device_location_data
    )

    # Get the max allowed age (seconds) requested by the user and compare it
    # with the simulated data age
    if simulated_data_age > verify_location_request.max_age:
        return DeviceLocationHelper.error_message_max_age_exceeded()

    # This API assumes that an UE are is always a circle, and never
    # a polygon
    # Get the radius of the simulated UE
    radius = DeviceLocationHelper.generate_random_radius(
        latitude=device_location_data.latitude,
        longitude=device_location_data.longitude
    )

    # Create a shapely circle area for the UE
    ue_area = DeviceLocationHelper.shapely_circle_from_coordinates_circle(
        center_latitude=device_location_data.latitude,
        center_longitude=device_location_data.longitude,
        radius_meters=radius
    )

    # Filter according to the area type
    if verify_location_request.area.area_type == "circle":
        shapely_desired_area = DeviceLocationHelper\
            .shapely_circle_from_coordinates_circle(
                center_latitude=verify_location_request.area.center.latitude,
                center_longitude=verify_location_request.area.center.longitude,
                radius_meters=verify_location_request.area.radius
            )
    # else -> its a polygon
    else:
        shapely_desired_area = DeviceLocationHelper\
            .shapely_polygon_from_list_of_coordinates_points(
                coordinates_points=verify_location_request.area.boundary
            )

    verification_result = DeviceLocationHelper\
        .compute_location_verification_result(
            device=ue_area,
            area=shapely_desired_area
        )

    # Update the UE timestamp
    verification_result.last_location_time = device_location_data.timestamp\
        .strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    return verification_result