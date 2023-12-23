# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 11:00:47
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-23 10:55:02

# flake8: noqa
from __future__ import annotations
from datetime import datetime
import re
from typing import List, Optional, Union, Any
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
    radius: float = Field(alias="radius", example="10")

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
    

class AreaEntered(BaseModel):

    device: Device = Field(alias="device")
    area: Area = Field(alias="area")
    subscription_id: str = Field(alias="subscriptionId")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class AreaLeft(BaseModel):

    device: Device = Field(alias="device")
    area: Area = Field(alias="area")
    subscription_id: str = Field(alias="subscriptionId")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CloudEvent(BaseModel):

    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(alias="datacontenttype", default=None)
    time: datetime = Field(alias="time")
    data: Optional[Any]

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CreateSubscription(BaseModel):

    webhook: Webhook = Field(alias="webhook")
    subscription_detail: SubscriptionDetail = Field(alias="subscriptionDetail")
    subscription_expire_time: Optional[datetime] = Field(
        alias="subscriptionExpireTime", default=None,
        example="2023-12-22T21:37:54.016Z"
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventAreaEntered(BaseModel):

    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(alias="datacontenttype", default=None)
    time: datetime = Field(alias="time")
    data: AreaEntered = Field(alias="data")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventAreaLeft(BaseModel):

    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(alias="datacontenttype", default=None)
    time: datetime = Field(alias="time")
    data: AreaLeft = Field(alias="data")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventSubscriptionEnds(BaseModel):

    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(alias="datacontenttype", default=None)
    time: datetime = Field(alias="time")
    data: SubscriptionEnds = Field(alias="data")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )



class SubscriptionCreationEventType(Enum):
    AREA_ENTERED = "org.camaraproject.geofencing.v0.area-entered"
    AREA_LEFT = "org.camaraproject.geofencing.v0.area-left"
    SUBSCRIPTION_ENDS = "org.camaraproject.geofencing.v0.subscription-ends"



class SubscriptionDetail(BaseModel):

    device: Device = Field(alias="device")
    area: Union[Circle, Polygon] = Field(alias="area")
    type: SubscriptionCreationEventType = Field(alias="type")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SubscriptionEnds(BaseModel):

    device: Device = Field(alias="device")
    area: Union[Circle, Polygon] = Field(alias="area")
    termination_reason: TerminationReason = Field(alias="terminationReason")
    subscription_id: str = Field(alias="subscriptionId")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SubscriptionEventType(Enum):
    AREA_ENTERED = "org.camaraproject.geofencing.v0.area-entered"
    AREA_LEFT = "org.camaraproject.geofencing.v0.area-left"
    SUBSCRIPTION_ENDS = "org.camaraproject.geofencing.v0.subscription-ends"


class SubscriptionInfo(BaseModel):

    webhook: Webhook = Field(alias="webhook")
    subscription_detail: SubscriptionDetail = Field(alias="subscriptionDetail")
    subscription_expire_time: Optional[datetime] = Field(
        alias="subscriptionExpireTime", default=None,
        example="2023-12-22T21:37:54.016Z"
    )
    subscription_id: str = Field(
        alias="subscriptionId", example="3fa85f64-5717-4562-b3fc-2c963f66afa6"
    )
    starts_at: Optional[datetime] = Field(
        alias="startsAt", default=None,  example="2023-12-20T21:37:54.016Z")
    expires_at: Optional[datetime] = Field(
        alias="expiresAt", default=None,  example="2023-12-22T21:37:54.016Z"
        )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class TerminationReason(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
    )


class Webhook(BaseModel):

    notification_url: str = Field(
        alias="notificationUrl", example="https://application-server.com"
    )
    notification_auth_token: Optional[str] = Field(
        alias="notificationAuthToken", default=None,
        example="c8974e592c2fa383d4a3960714"
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )



class AreaType(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True,
    )


AreaType.model_rebuild()
Webhook.model_rebuild()
TerminationReason.model_rebuild()
SubscriptionInfo.model_rebuild()
SubscriptionEnds.model_rebuild()
SubscriptionDetail.model_rebuild()
EventSubscriptionEnds.model_rebuild()
EventAreaLeft.model_rebuild()
EventAreaEntered.model_rebuild()
CreateSubscription.model_rebuild()
CloudEvent.model_rebuild()
AreaLeft.model_rebuild()
AreaEntered.model_rebuild()
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
