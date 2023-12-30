# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-27 11:11:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-30 20:34:42
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ErrorResponse(BaseModel):

    code: Optional[str] = Field(alias="code", default=None)
    status: Optional[int] = Field(alias="status", default=None)
    message: Optional[str] = Field(alias="message", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
    )


class MecPlatform(BaseModel):
    edge_cloud_provider: str = Field(
        alias="edgeCloudProvider", default=None, example="Altice"
    )
    edge_resource_name: str = Field(
        alias="edgeResourceName", default=None, example="alb-wl1-ave-wlz-012"
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class MecPlatforms(List[MecPlatform]):
    pass


MecPlatform.model_rebuild()
ErrorResponse.model_rebuild()
