# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-14 11:14:04
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 11:16:37
from fastapi.responses import JSONResponse
import config # noqa
from common.apis.sim_swap_schemas import ErrorInfo
from common.apis.device_status_schemas import (
    ConnectivityStatus,
)


def error_message_simulation_not_running():
    return JSONResponse(
            status_code=412,
            content=ErrorInfo(
                status=412,
                code="SIMULATION.NOT_RUNNING",
                message="The simulation is not running. Thus, you cannot " +
                "get its generated data"
            ).__dict__
        )


def error_message_unknown_device():
    return JSONResponse(
            status_code=404,
            content=ErrorInfo(
                status=404,
                code="NOT_FOUND",
                message="The specified resource is not found."
            ).__dict__
        )


def get_connectivity_enum_from_value(value):
    for status in ConnectivityStatus:
        if status.value == value:
            return status
