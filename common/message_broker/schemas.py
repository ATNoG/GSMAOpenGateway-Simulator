# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 15:40:18
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-21 14:48:22
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from common.simulation.simulation_types import SimulationType
from common.simulation.simulation_operations import SimulationOperation
from common.subscriptions.subscription_types import SubscriptionType
from common.apis.device_location_schemas import (
    Area,
    Webhook,
    SubscriptionEventType
)
from enum import Enum


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
    scope: str = Field(default="SIMULATION_DATA")


class Subscription(BaseModel):
    simulation_id: int
    subscription_id: int
    subscription_type: SubscriptionType


class GeofencingSubscription(Subscription):
    area: Area
    geofencing_subscription_type: SubscriptionEventType
    ue: int
    webhook: Webhook
    expire_time: datetime
    ue_inside_geofence: Optional[bool] = Field(default=None)


class GeofencingSubscriptionEventOperation(Enum):
    add = "ADD"
    delete = "DELETE"


class GeofencingSubscriptionEvent(BaseModel):
    operation: GeofencingSubscriptionEventOperation
    subscriptions: List[GeofencingSubscription]
    scope: str = Field(default="SUBSCRIPTIONS")
