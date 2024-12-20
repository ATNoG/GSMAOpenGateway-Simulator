# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-08 15:11:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-10 12:03:08
import uuid
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    event
)
from common.database.database import Base
from datetime import datetime


class Simulation(Base):
    __tablename__ = "simulation"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    duration_seconds = Column(Integer)
    payload = Column(String)


class SimulationInstance(Base):
    __tablename__ = "simulation_instance"

    id = Column(Integer, primary_key=True, index=True)
    root_simulation = Column(
        Integer, ForeignKey("simulation.id"), nullable=False
    )
    # duration_seconds = max duration of all child simulations
    duration_seconds = Column(Integer)
    # start_timestamp -> If NULL -> simulation not still running
    start_timestamp = Column(DateTime(timezone=True))
    # end_timestamp -> If NULL -> simulation still running
    end_timestamp = Column(DateTime(timezone=True))


class ChildSimulationInstance(Base):
    __tablename__ = "child_simulation_instance"
    id = Column(Integer, primary_key=True, index=True)
    simulation_instance = Column(
        Integer, ForeignKey("simulation_instance.id"), nullable=False
    )
    simulation_type = Column(String)
    duration_seconds = Column(Integer)
    # start_timestamp -> If NULL -> simulation not still running
    start_timestamp = Column(DateTime(timezone=True))
    # end_timestamp -> If NULL -> simulation still running
    end_timestamp = Column(DateTime(timezone=True))


class SimulationUE(Base):
    __tablename__ = "simulation_ue"

    id = Column(Integer, primary_key=True, index=True)
    root_simulation = Column(
        Integer, ForeignKey("simulation.id"), nullable=False
    )
    phone_number = Column(String)
    network_access_identifier = Column(String)
    ipv4_address_public_address = Column(String)
    ipv4_address_private_address = Column(String)
    ipv4_address_public_port = Column(Integer)
    ipv6_address = Column(String)


class SimulationUEInstance(Base):
    __tablename__ = "simulation_ue_instance"

    id = Column(Integer, primary_key=True, index=True)
    simulation_instance = Column(
        Integer, ForeignKey("simulation_instance.id"), nullable=False
    )
    simulation_ue = Column(
        Integer, ForeignKey("simulation_ue.id"), nullable=False
    )


class DeviceLocationSimulationData(Base):
    __tablename__ = "device_location_simulation_data"

    id = Column(Integer, primary_key=True, index=True)
    child_simulation_instance = Column(
        Integer, ForeignKey("child_simulation_instance.id"), nullable=False,
        index=True
    )
    simulation_instance = Column(
        Integer, ForeignKey("simulation_instance.id"), nullable=False
    )
    ue = Column(
        Integer, ForeignKey("simulation_ue_instance.id"), nullable=False
    )
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime(timezone=True))


class DeviceLocationSubscription(Base):
    __tablename__ = "device_location_subscription"

    id = Column(
        String, primary_key=True, index=True,
        unique=True, nullable=False
    )
    root_simulation = Column(
        Integer, ForeignKey("simulation.id"), nullable=False
    )
    ue = Column(
        Integer, ForeignKey("simulation_ue.id"), nullable=False
    )
    area = Column(String)  # Receives the area as a JSON
    subscription_type = Column(String)
    webhook_url = Column(String)
    webhook_auth_token = Column(String)
    start_time = Column(DateTime(timezone=True))
    expire_time = Column(DateTime(timezone=True))


class DeviceLocationSubscriptionNotification(Base):
    __tablename__ = "device_location_subscription_notification"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(
        String, ForeignKey("device_location_subscription.id"), nullable=False
    )
    sucess = Column(Boolean, nullable=True, default=None)
    error = Column(String, nullable=True, default=None)


class SimSwapSimulationData(Base):
    __tablename__ = "sim_swap_simulation_data"

    id = Column(Integer, primary_key=True, index=True)
    child_simulation_instance = Column(
        Integer, ForeignKey("child_simulation_instance.id"), nullable=False,
        index=True
    )
    simulation_instance = Column(
        Integer, ForeignKey("simulation_instance.id"), nullable=False
    )
    ue = Column(
        Integer, ForeignKey("simulation_ue_instance.id"), nullable=False
    )
    new_msisdn = Column(String)
    timestamp = Column(DateTime(timezone=True))


class SimulationMecPlatform(Base):
    __tablename__ = "simulation_mec_platform"

    id = Column(Integer, primary_key=True, index=True)
    root_simulation = Column(
        Integer, ForeignKey("simulation.id"), nullable=False
    )
    edge_cloud_provider = Column(String)
    edge_resource_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)


class DeviceStatusSimulationData(Base):
    __tablename__ = "device_status_simulation_data"

    id = Column(Integer, primary_key=True, index=True)
    child_simulation_instance = Column(
        Integer, ForeignKey("child_simulation_instance.id"), nullable=False,
        index=True
    )
    simulation_instance = Column(
        Integer, ForeignKey("simulation_instance.id"), nullable=False
    )
    ue = Column(
        Integer, ForeignKey("simulation_ue_instance.id"), nullable=False
    )
    connectivity_status = Column(String)
    roaming = Column(Boolean)
    country_code = Column(Integer)
    # Will receive a list of strings parsed to json
    country_name = Column(String)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)


class DeviceStatusSubscription(Base):
    __tablename__ = "device_status_subscription"

    id = Column(
        String, primary_key=True, index=True,
        unique=True, nullable=False
    )
    root_simulation = Column(
        Integer, ForeignKey("simulation.id"), nullable=False
    )
    ue = Column(
        Integer, ForeignKey("simulation_ue.id"), nullable=False
    )
    subscription_type = Column(String)
    webhook_url = Column(String)
    webhook_auth_token = Column(String)
    start_time = Column(DateTime(timezone=True))
    expire_time = Column(DateTime(timezone=True))


class DeviceStatusSubscriptionNotification(Base):
    __tablename__ = "device_status_subscription_notification"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(
        String, ForeignKey("device_status_subscription.id"), nullable=False
    )
    sucess = Column(Boolean, nullable=True, default=None)
    error = Column(String, nullable=True, default=None)


@event.listens_for(DeviceLocationSubscription, 'before_insert')
@event.listens_for(DeviceStatusSubscription, 'before_insert')
def before_insert(mapper, connection, target):
    target.id = str(uuid.uuid4())
