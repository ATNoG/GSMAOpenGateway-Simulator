# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 15:40:18
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-13 19:51:56
from pydantic import BaseModel, Field
from typing import Any, Optional
from common.simulation.simulation_types import SimulationType
from common.simulation.simulation_operations import SimulationOperation


class SimulationAction(BaseModel):
    action: SimulationOperation
    simulation_type: SimulationType
    simulation_instance_id: int
    child_simulation_instance_id: int
    simulation_config: Optional[dict] = Field(default=None)


class DeviceLocationSimulationData(BaseModel):
    ue: int
    latitude: float = Field(..., ge=-90, le=90,
                            description="Valid range: -90 to 90")
    longitude: float = Field(..., ge=-180, le=180,
                             description="Valid range: -180 to 180")
    timestamp: str


class SimulationData(BaseModel):
    simulation_id: int
    child_simulation_id: int
    simulation_type: SimulationType
    data: Any
