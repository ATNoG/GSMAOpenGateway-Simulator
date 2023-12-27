# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-27 11:11:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 20:31:44
from __future__ import annotations
from datetime import datetime
import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, ConfigDict


class ErrorResponse(BaseModel):

    code: Optional[str] = Field(alias="code", default=None)
    status: Optional[int] = Field(alias="status", default=None)
    message: Optional[str] = Field(alias="message", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
    )


class MecPlatform(BaseModel):
    edge_cloud_provider: Optional[str] = Field(
        alias="edgeCloudProvider", default=None
    )
    edge_resource_name: Optional[Dict[str, Any]] = Field(
        alias="edgeResourceName", default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class MecPlatforms(List[MecPlatform]):
    pass


MecPlatform.model_rebuild()
ErrorResponse.model_rebuild()
