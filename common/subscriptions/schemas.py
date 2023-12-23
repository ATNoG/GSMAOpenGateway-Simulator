# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-11 15:40:18
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 21:21:22
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Union
from common.subscriptions.subscription_types import SubscriptionType
from common.apis.device_location_schemas import (
    Circle,
    Polygon,
    Webhook,
    SubscriptionEventType
)
from enum import Enum


class Subscription(BaseModel):
    simulation_id: int
    subscription_id: str
    subscription_type: SubscriptionType


class GeofencingSubscription(Subscription):
    area: Union[Circle, Polygon]
    geofencing_subscription_type: SubscriptionEventType
    ue: int
    webhook: Webhook
    expire_time: datetime
    ue_inside_geofence: Optional[bool] = Field(default=None)


class GeofencingSubscriptionEventOperation(Enum):
    add = "ADD"
    delete = "DELETE"


class GeofencingSubscriptionEvent(BaseModel):
    simulation_id: int
    operation: GeofencingSubscriptionEventOperation
    subscriptions: List[GeofencingSubscription]
    scope: str = Field(default="GEOFENCING_SUBSCRIPTIONS")
