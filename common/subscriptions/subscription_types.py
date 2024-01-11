# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:10:25
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 17:58:19

from enum import Enum


class SubscriptionType(Enum):
    DEVICE_LOCATION_GEOFENCING = "DEVICE_LOCATION_GEOFENCING"
    DEVICE_STATUS = "DEVICE_STATUS"
