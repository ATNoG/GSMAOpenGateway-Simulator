# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:10:25
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-08 10:48:50

from enum import Enum


class SimulationType(Enum):
    DEVICE_LOCATION = "DEVICE_LOCATION"
    SIM_SWAP = "SIM_SWAP"
    SIMPLE_EDGE_DISCOVERY = "SIMPLE_EDGE_DISCOVERY"
    DEVICE_STATUS = "DEVICE_STATUS"
