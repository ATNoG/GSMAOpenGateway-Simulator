# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 15:40:18
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 10:31:25
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Union
from common.simulation.simulation_types import SimulationType
from common.simulation.simulation_operations import SimulationOperation
from common.subscriptions.subscription_types import SubscriptionType
from common.apis.device_location_schemas import (
    Circle,
    Polygon,
    Webhook,
    SubscriptionEventType
)
from enum import Enum


class SimulationAction(BaseModel):
    action: SimulationOperation
    simulation_type: SimulationType
    simulation_id: int
    simulation_instance_id: int
    child_simulation_instance_id: int
    simulation_config: Optional[dict] = Field(default=None)


class DeviceLocationSimulationData(BaseModel):
    ue: int
    ue_instance: int
    latitude: float = Field(..., ge=-90, le=90,
                            description="Valid range: -90 to 90")
    longitude: float = Field(..., ge=-180, le=180,
                             description="Valid range: -180 to 180")
    timestamp: str


class SIMSwapSimulationData(BaseModel):
    ue: int
    ue_instance: int
    new_msisdn: str
    timestamp: str


class SimulationData(BaseModel):
    simulation_id: int
    simulation_instance_id: int
    child_simulation_instance_id: int
    simulation_type: SimulationType
    data: Any  # Union in the future
    scope: str = Field(default="SIMULATION_DATA")


class Subscription(BaseModel):
    simulation_id: int
    subscription_id: str
    subscription_type: SubscriptionType
