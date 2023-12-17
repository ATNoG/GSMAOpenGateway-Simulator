# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-08 15:11:23
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-17 16:52:09

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Float
)
from common.database.database import Base


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
    simulation_instance = Column(
        Integer, ForeignKey("simulation_instance.id"), nullable=False
    )
    phone_number = Column(String)
    network_access_identifier = Column(String)
    ipv4_address_public_address = Column(String)
    ipv4_address_private_address = Column(String)
    ipv4_address_public_port = Column(Integer)
    ipv6_address = Column(String)


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
        Integer, ForeignKey("simulation_ue.id"), nullable=False
    )
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime(timezone=True))