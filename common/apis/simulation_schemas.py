# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 11:00:47
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 20:54:56

from __future__ import annotations
from typing import List, Union, Optional
from pydantic import BaseModel, Field, ConfigDict, validator
import config # noqa
from common.apis.device_location_schemas import Device, Point
from common.simulation.simulation_types import SimulationType
from common.apis.simple_edge_discovery_schemas import MecPlatform


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
    mec_platforms: Optional[List[SimulationMecPlatform]] = Field(default=[])
    child_simulations: List[
        Union[
            SIMSwapSimulation,
            DeviceLocationSimulation
        ]
    ]


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
    simulation_type: str = Field(
        default=SimulationType.SIM_SWAP.value
    )
    devices: List[str]
    timestamps_for_swaps_seconds: List[float]


class ItineraryStop(Point):
    label: str


class SimulationMecPlatform(MecPlatform):

    latitude: float = Field(alias="latitude")
    longitude: float = Field(alias="longitude")

    @validator("latitude")
    def latitude_max(cls, value):
        assert value <= 90
        return value

    @validator("latitude")
    def latitude_min(cls, value):
        assert value >= -90
        return value

    @validator("longitude")
    def longitude_max(cls, value):
        assert value <= 180
        return value

    @validator("longitude")
    def longitude_min(cls, value):
        assert value >= -180
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


Point.model_rebuild()
Device.model_rebuild()
SimulationUE.model_rebuild()
RootSimulationCreate.model_rebuild()
RootSimulationCreateResponse.model_rebuild()
DeviceLocationSimulation.model_rebuild()
ItineraryStop.model_rebuild()
SimulationMecPlatform.model_rebuild()
