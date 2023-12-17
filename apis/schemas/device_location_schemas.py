# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 11:00:47
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-17 19:25:55

# flake8: noqa
from __future__ import annotations
from datetime import datetime
import re
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum


class Area(BaseModel):

    area_type: str = Field(alias="areaType")


class Circle(Area):

    area_type: str = Field(alias="areaType", default="circle")
    center: Point = Field(alias="center", default=None, example={
                "latitude":40.6295718,
                "longitude":-8.6569065,
            })
    radius: float = Field(alias="radius")

    @validator("radius")
    def radius_min(cls, value):
        assert value >= 1
        return value


class DeviceIpv4Addr(BaseModel):

    public_address: Optional[str] = Field(
        alias="publicAddress", default=None, example="10.93.125.84"
    )
    private_address: Optional[str] = Field(
        alias="privateAddress", default=None, example="10.10.10.10"
        )
    public_port: Optional[int] = Field(
        alias="publicPort", default=None, example=56795
        )

    @validator("public_address")
    def public_address_pattern(cls, value):
        assert value is not None and re.match(r"^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$", value)
        return value

    @validator("private_address")
    def private_address_pattern(cls, value):
        assert value is not None and re.match(r"^(([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$", value)
        return value

    @validator("public_port")
    def public_port_max(cls, value):
        assert value <= 65535
        return value

    @validator("public_port")
    def public_port_min(cls, value):
        assert value >= 0
        return value


class Device(BaseModel):

    phone_number: str = Field(
        alias="phoneNumber", example="123456789"
    )
    network_access_identifier: Optional[str] = Field(
        alias="networkAccessIdentifier", default=None,
        example="10.93.125.84m"
    )
    ipv4_address: Optional[DeviceIpv4Addr] = Field(
        alias="ipv4Address", default=None
    )
    ipv6_address: Optional[str] = Field(
        alias="ipv6Address", default=None,
        example="2001:db6:85a3:8d3:1319:8a2e:111:7344"
    )

    @validator("phone_number")
    def phone_number_pattern(cls, value):
        assert value is not None and re.match(r"^\+?\d{5,15}$", value)
        return value

    @validator("ipv6_address")
    def ipv6_address_pattern(cls, value):
        assert value is not None and re.match(r"^((:|(0?|([1-9a-f][0-9a-f]{0,3}))):)((0?|([1-9a-f][0-9a-f]{0,3})):){0,6}(:|(0?|([1-9a-f][0-9a-f]{0,3})))(\/((\d)|(\d{2})|(1[0-1]\d)|(12[0-8])))?$", value)
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


class TokenModel(BaseModel):

    sub: str


class Ipv6Address(BaseModel):
    pass

    
class Point(BaseModel):

    latitude: float = Field(alias="latitude")
    longitude: float = Field(alias="longitude")

    @validator("latitude")
    def latitude_max(cls, value):
        assert value <= 90
        return value

    @validator("latitude")
    def latitude_min(cls, value):
        assert value >= -90
        return value

    @validator("longitude")
    def longitude_max(cls, value):
        assert value <= 180
        return value

    @validator("longitude")
    def longitude_min(cls, value):
        assert value >= -180
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )
     
class Polygon(Area):

    area_type: str = Field(alias="areaType", default="polygon")
    boundary: List[Point] = Field(alias="boundary")



class Location(BaseModel):

    last_location_time: str = Field(
        alias="lastLocationTime", example="2023-10-17T13:18:23.682Z"
    )
    area: Union[Polygon, Circle] = Field(
        alias="area", default=None, example=Circle(
                center=Point(latitude=47.497913, longitude=19.040236),
                radius=800
            )
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )
class RetrievalLocationRequest(BaseModel):

    device: Device = Field(alias="device")
    max_age: Optional[int] = Field(
        alias="maxAge", default=60, example=60
    )

    @validator("max_age")
    def max_age_min(cls, value):
        assert value >= 60
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class VerificationResult(Enum):
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"
    PARTIAL = "PARTIAL" 



class VerifyLocationRequest(BaseModel):

    device: Device = Field(alias="device")
    area: Union[Polygon, Circle] = Field(
        alias="area", example=Circle(
                center=Point(latitude=47.497913, longitude=19.040236),
                radius=20
            )
        )
    max_age: Optional[float] = Field(
        alias="maxAge", default=None, example=120
        )

    @validator("max_age")
    def max_age_min(cls, value):
        assert value >= 60
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class VerifyLocationResponse(BaseModel):

    last_location_time: str = Field(
        alias="lastLocationTime", example="2023-10-17T13:18:23.682Z"
    )
    verification_result: VerificationResult = Field(alias="verificationResult")
    match_rate: Optional[int] = Field(alias="matchRate", default=None)

    @validator("match_rate")
    def match_rate_max(cls, value):
        assert value <= 99
        return value

    @validator("match_rate")
    def match_rate_min(cls, value):
        assert value >= 1
        return value
    
    model_config = ConfigDict(
        populate_by_name=True,
    )
    


VerifyLocationResponse.model_rebuild()
VerifyLocationRequest.model_rebuild()
RetrievalLocationRequest.model_rebuild()
Polygon.model_rebuild()
Point.model_rebuild()
Location.model_rebuild()
Ipv6Address.model_rebuild()
ErrorInfo.model_rebuild()
Device.model_rebuild()
DeviceIpv4Addr.model_rebuild()
Circle.model_rebuild()
Area.model_rebuild()
