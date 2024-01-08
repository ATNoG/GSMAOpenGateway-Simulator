# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2024-01-08 10:00:17
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-08 10:57:17
# coding: utf-8

from __future__ import annotations
from datetime import datetime
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, validator
from enum import Enum


class BasicDeviceEventData(BaseModel):
    device: Device = Field(alias="device")
    subscription_id: Optional[str] = Field(
        alias="subscriptionId",
        default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class CloudEvent(BaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: Dict[str, Any] = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ConnectivityStatusResponse(BaseModel):
    connectivity_status: ConnectivityStatus = Field(alias="connectivityStatus")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ConnectivityStatus(Enum):
    CONNECTED_SMS = "CONNECTED_SMS"
    CONNECTED_DATA = "CONNECTED_DATA"
    NOT_CONNECTED = "NOT_CONNECTED"


class CreateSubscription(BaseModel):
    subscription_detail: SubscriptionDetail = Field(alias="subscriptionDetail")
    subscription_expire_time: Optional[datetime] = Field(
        alias="subscriptionExpireTime", default=None
    )
    webhook: Webhook = Field(alias="webhook")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class DeviceIpv4Addr(BaseModel):

    public_address: Optional[str] = Field(
        alias="publicAddress", default=None
    )
    private_address: Optional[str] = Field(
        alias="privateAddress", default=None
    )
    public_port: Optional[int] = Field(
        alias="publicPort", default=None
    )

    @validator("public_port")
    def public_port_max(cls, value):
        assert value <= 65535
        return value

    @validator("public_port")
    def public_port_min(cls, value):
        assert value >= 0
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class Device(BaseModel):

    phone_number: str = Field(
        alias="phoneNumber", example="123456789"
    )
    network_access_identifier: Optional[str] = Field(
        alias="networkAccessIdentifier", default=None
    )
    ipv4_address: Optional[DeviceIpv4Addr] = Field(
        alias="ipv4Address", default=None,
        example="10.10.10.84"
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
        assert value is not None and re.match(r"^((:|(0?|([1-9a-f][0-9a-f]{0,3}))):)((0?|([1-9a-f][0-9a-f]{0,3})):){0,6}(:|(0?|([1-9a-f][0-9a-f]{0,3})))(\/((\d)|(\d{2})|(1[0-1]\d)|(12[0-8])))?$", value)  # noqa
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


class EventConnectivityData(BaseModel):

    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: BasicDeviceEventData = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventConnectivityDisconnected(BaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: BasicDeviceEventData = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventConnectivitySms(BaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: BasicDeviceEventData = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventRoamingChangeCountry(BaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: RoamingChangeCountry = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventRoamingOff(BaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: BasicDeviceEventData = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventRoamingOn(BaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: BasicDeviceEventData = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class EventRoamingStatus(BaseModel):
    id: str = Field(alias="id")
    source: str = Field(alias="source")
    type: SubscriptionEventType = Field(alias="type")
    specversion: str = Field(alias="specversion")
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: RoamingStatus = Field(alias="data")
    time: datetime = Field(alias="time")

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
    datacontenttype: Optional[str] = Field(
        alias="datacontenttype", default=None
    )
    data: SubscriptionEnds = Field(alias="data")
    time: datetime = Field(alias="time")

    @validator("source")
    def source_min_length(cls, value):
        assert len(value) >= 1
        return value

    model_config = ConfigDict(
        populate_by_name=True,
    )


class RequestConnectivityStatus(BaseModel):
    device: Device = Field(alias="device")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class RequestRoamingStatus(BaseModel):
    device: Device = Field(alias="device")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class RoamingChangeCountry(BaseModel):
    device: Device = Field(alias="device")
    country_code: Optional[int] = Field(alias="countryCode", default=None)
    country_name: Optional[List[str]] = Field(
        alias="countryName", default=None
    )
    subscription_id: Optional[str] = Field(
        alias="subscriptionId", default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class RoamingStatusResponse(BaseModel):
    roaming: bool = Field(alias="roaming")
    country_code: Optional[int] = Field(alias="countryCode", default=None)
    country_name: Optional[List[str]] = Field(
        alias="countryName", default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class RoamingStatus(BaseModel):
    device: Device = Field(alias="device")
    roaming: bool = Field(alias="roaming")
    country_code: Optional[int] = Field(alias="countryCode", default=None)
    country_name: Optional[List[str]] = Field(
        alias="countryName", default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SubscriptionAsync(BaseModel):
    subscription_id: Optional[str] = Field(
        alias="subscriptionId", default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SubscriptionCreationEventType(Enum):
    ROAMING_STATUS = "org.camaraproject.device-status.v0.roaming-status"
    ROAMING_ON = "org.camaraproject.device-status.v0.roaming-on"
    ROAMING_OFF = "org.camaraproject.device-status.v0.roaming-off"
    ROAMING_CHANGE_COUNTRY = "org.camaraproject.device-status.v0."\
        "roaming-change-country"
    CONNECTIVITY_DATA = "org.camaraproject.device-status.v0.connectivity-data"
    CONNECTIVITY_SMS = "org.camaraproject.device-status.v0.connectivity-sms"
    CONNECTIVITY_DISCONNECTED = "org.camaraproject.device-status.v0."\
        "connectivity-disconnected"
    SUBSCRIPTION_ENDS = "org.camaraproject.device-status.v0.subscription-ends"


class SubscriptionDetail(BaseModel):
    device: Device = Field(alias="device")
    type: SubscriptionCreationEventType = Field(alias="type")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SubscriptionEnds(BaseModel):
    device: Device = Field(alias="device")
    termination_reason: str = Field(alias="terminationReason")
    subscription_id: Optional[str] = Field(
        alias="subscriptionId", default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SubscriptionEventType(Enum):
    ROAMING_STATUS = "org.camaraproject.device-status.v0.roaming-status"
    ROAMING_ON = "org.camaraproject.device-status.v0.roaming-on"
    ROAMING_OFF = "org.camaraproject.device-status.v0.roaming-off"
    ROAMING_CHANGE_COUNTRY = "org.camaraproject.device-status.v0."\
        "roaming-change-country"
    CONNECTIVITY_DATA = "org.camaraproject.device-status.v0.connectivity-data"
    CONNECTIVITY_SMS = "org.camaraproject.device-status.v0.connectivity-sms"
    CONNECTIVITY_DISCONNECTED = "org.camaraproject.device-status.v0."\
        "connectivity-disconnected"
    SUBSCRIPTION_ENDS = "org.camaraproject.device-status.v0.subscription-ends"


class SubscriptionInfo(BaseModel):
    subscription_detail: SubscriptionDetail = Field(alias="subscriptionDetail")
    subscription_expire_time: Optional[datetime] = Field(
        alias="subscriptionExpireTime", default=None
    )
    webhook: Webhook = Field(alias="webhook")
    subscription_id: str = Field(alias="subscriptionId")
    starts_at: Optional[datetime] = Field(alias="startsAt", default=None)
    expires_at: Optional[datetime] = Field(alias="expiresAt", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
    )


class Webhook(BaseModel):
    notification_url: str = Field(alias="notificationUrl")
    notification_auth_token: Optional[str] = Field(
        alias="notificationAuthToken", default=None
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )


Webhook.model_rebuild()
SubscriptionInfo.model_rebuild()
SubscriptionEnds.model_rebuild()
SubscriptionDetail.model_rebuild()
SubscriptionAsync.model_rebuild()
RoamingStatus.model_rebuild()
RoamingStatusResponse.model_rebuild()
RequestRoamingStatus.model_rebuild()
RoamingChangeCountry.model_rebuild()
RequestConnectivityStatus.model_rebuild()
EventSubscriptionEnds.model_rebuild()
EventRoamingStatus.model_rebuild()
EventRoamingOn.model_rebuild()
EventRoamingOff.model_rebuild()
EventRoamingChangeCountry.model_rebuild()
EventConnectivitySms.model_rebuild()
EventConnectivityDisconnected.model_rebuild()
EventConnectivityData.model_rebuild()
ErrorInfo.model_rebuild()
Device.model_rebuild()
DeviceIpv4Addr.model_rebuild()
CreateSubscription.model_rebuild()
ConnectivityStatusResponse.model_rebuild()
CloudEvent.model_rebuild()
BasicDeviceEventData.model_rebuild()
