# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 11:14:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-30 18:07:47


from fastapi.responses import JSONResponse
import config # noqa
from common.database import models
from common.apis.simple_edge_discovery_schemas import ErrorResponse
from typing import List
from geopy.distance import geodesic
from common.apis.simple_edge_discovery_schemas import ErrorResponse
import logging


def error_message_simulation_not_running():
    return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                status=404,
                code="SIMULATION.NOT_RUNNING",
                message="The simulation is not running. Thus, you cannot " +
                "get its generated data"
            ).__dict__
        )


def error_message_simulation_is_starting():
    return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                status=404,
                code="SIMULATION.IS_STARTING",
                message="The simulation is still starting. Thus, you cannot " +
                "get its generated data"
            ).__dict__
        )


def error_message_device_not_found():
    return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                status=404,
                code="NOT_FOUND",
                message="No device found for the specified parameters"
            ).__dict__
        )


def error_message_insufficient_parameters():
    return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                status=400,
                code="INVALID_ARGUMENT",
                message="Insufficient parameters: At least one of " +
                "Network-Access-Identifier, Phone-Number or IP-Address must " +
                "be specified, or, the API must be called by a client on a " +
                "netwok-attached device (hence passing the source IP in the " +
                "request header)"
            ).__dict__
        )


def get_closest_mec_platform(
    mec_platforms: List[models.SimulationMecPlatform],
    device_location_simulation_data: models.DeviceLocationSimulationData
):
    min_distance = None
    closest_mec_platform = None
    for mec_platform in mec_platforms:
        distance_meters = geodesic(
            (
                mec_platform.latitude,
                mec_platform.longitude
            ),
            (
                device_location_simulation_data.latitude,
                device_location_simulation_data.longitude
            )
        ).meters

        logging.info(
            "The distance between the UE Instance with ID "
            f"{device_location_simulation_data.ue} (lat: "
            f"{device_location_simulation_data.latitude}, long: "
            f"{device_location_simulation_data.longitude}) and the MEC "
            f"Platform with ID {mec_platform.id} (edge_resource_name: "
            f"{mec_platform.edge_resource_name}, edge_cloud_provider: "
            f"{mec_platform.edge_cloud_provider}, lat: "
            f"{mec_platform.latitude}, long: {mec_platform.longitude}) is of "
            f"{distance_meters} meters."
            )

        # Update the closes MEC
        if min_distance is None or distance_meters < min_distance:
            min_distance = distance_meters
            closest_mec_platform = mec_platform

    return closest_mec_platform
