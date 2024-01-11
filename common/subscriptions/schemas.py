# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 15:40:18
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 19:29:39
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Union
from common.subscriptions.subscription_types import SubscriptionType
from common.apis.device_location_schemas import (
    Circle,
    Polygon,
    Webhook as DeviceLocationWebhook,
    SubscriptionEventType as DeviceLocationSubscriptionEventType
)
from common.apis.device_status_schemas import (
    SubscriptionEventType as DeviceStatusSubscriptionEventType,
    Webhook as DeviceStatusWebhook,
)
from enum import Enum


class Subscription(BaseModel):
    simulation_id: int
    subscription_id: str
    subscription_type: SubscriptionType


class GeofencingSubscription(Subscription):
    area: Union[Circle, Polygon]
    geofencing_subscription_type: DeviceLocationSubscriptionEventType
    ue: int
    webhook: DeviceLocationWebhook
    expire_time: datetime
    ue_inside_geofence: Optional[bool] = Field(default=None)


class DeviceStatusSubscription(Subscription):
    device_status_subscription_type: DeviceStatusSubscriptionEventType
    ue: int
    webhook: DeviceStatusWebhook
    expire_time: datetime
    current_connectivity_status: str
    current_country_code: int
    current_roaming: bool
    current_country_name: List[str]


class GeofencingSubscriptionEventOperation(Enum):
    add = "ADD"
    delete = "DELETE"


class GeofencingSubscriptionEvent(BaseModel):
    simulation_id: int
    operation: GeofencingSubscriptionEventOperation
    subscriptions: List[GeofencingSubscription]
    scope: str = Field(default="GEOFENCING_SUBSCRIPTIONS")
