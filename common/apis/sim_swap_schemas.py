# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-27 11:11:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 11:38:48
from __future__ import annotations
from datetime import datetime
import re
from typing import Optional
from pydantic import BaseModel, Field, validator, ConfigDict


class CheckSimSwapInfo(BaseModel):
    swapped: Optional[bool] = Field(alias="swapped", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CreateCheckSimSwap(BaseModel):

    phone_number: str = Field(
        alias="phoneNumber", example="+346661113334"
    )
    max_age: Optional[int] = Field(
        alias="maxAge", default=None, example=60
    )

    @validator("phone_number")
    def phone_number_pattern(cls, value):
        assert value is not None and re.match(r"\+?\d{5,15}", value)
        return value

    @validator("max_age")
    def max_age_max(cls, value):
        assert value <= 2400
        return value

    @validator("max_age")
    def max_age_min(cls, value):
        assert value >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CreateSimSwapDate(BaseModel):

    phone_number: str = Field(
        alias="phoneNumber", example="+346661113334"
    )

    @validator("phone_number")
    def phone_number_pattern(cls, value):
        assert value is not None and re.match(r"\+?\d{5,15}", value)
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ErrorInfo(BaseModel):

    status: int = Field(alias="status")
    code: str = Field(alias="code")
    message: str = Field(alias="message")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SimSwapInfo(BaseModel):

    latest_sim_change: Optional[datetime] = Field(
        alias="latestSimChange", default=None, example=True
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


SimSwapInfo.model_rebuild()
ErrorInfo.model_rebuild()
CreateSimSwapDate.model_rebuild()
CreateCheckSimSwap.model_rebuild()
CheckSimSwapInfo.model_rebuild()
