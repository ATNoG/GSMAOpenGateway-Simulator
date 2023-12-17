# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 11:00:47
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-17 19:02:09

from __future__ import annotations
from typing import List, Union
from pydantic import BaseModel, Field, ConfigDict
import config # noqa
from schemas.device_location_schemas import Device, Point
from common.simulation.simulation_types import SimulationType


class SimulationUE(Device):
    # Equal to the device location Device schema
    id: str
    model_config = ConfigDict(
        populate_by_name=True,
    )


class RootSimulationCreate(BaseModel):

    name: str
    description: str
    devices: List[SimulationUE]
    child_simulations: List[Union[SIMSwapSimulation, DeviceLocationSimulation]]


class RootSimulationCreateResponse(RootSimulationCreate):

    id: int
    duration_seconds: int


class DeviceLocationSimulation(BaseModel):
    simulation_type: str = Field(
        default=SimulationType.DEVICE_LOCATION.value
    )
    devices: List[str]
    duration: int  # in seconds
    itinerary: List[ItineraryStop]


class SIMSwapSimulation(BaseModel):
    sim: str


class ItineraryStop(Point):
    label: str


Point.model_rebuild()
Device.model_rebuild()
SimulationUE.model_rebuild()
RootSimulationCreate.model_rebuild()
RootSimulationCreateResponse.model_rebuild()
DeviceLocationSimulation.model_rebuild()
ItineraryStop.model_rebuild()
