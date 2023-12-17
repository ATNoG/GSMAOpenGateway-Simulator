# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-08 17:51:02
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-17 16:38:36

from sqlalchemy.orm import Session
from common.database import models
from common.simulation.simulation_types import SimulationType
import logging
import json


def create_simulation(
    db: Session, name, description, duration_seconds, payload
):
    # Create a new Simulation instance
    new_simulation = models.Simulation(
        name=name,
        description=description,
        duration_seconds=duration_seconds,
        payload=payload
    )

    db.add(new_simulation)
    db.commit()
    db.refresh(new_simulation)

    logging.info(
        f"Created simulation with id {new_simulation.id}."
    )
    return new_simulation


def get_simulation(
    db: Session, simulation_id: int
):
    simulation = db.query(models.Simulation).filter(
        models.Simulation.id == simulation_id
    ).first()

    logging.info(f"Got simulation with id {simulation_id}.")

    return simulation


def create_simulation_instance(
    db: Session, name, description, duration_seconds, start_timestamp=None,
    end_timestamp=None
):
    # Create a new Simulation instance
    new_simulation_instance = models.SimulationInstance(
        name=name,
        description=description,
        duration_seconds=duration_seconds
    )

    # Fill in non-mandatory fields
    if start_timestamp:
        new_simulation_instance.start_timestamp = start_timestamp
    if end_timestamp:
        new_simulation_instance.end_timestamp = end_timestamp

    db.add(new_simulation_instance)
    db.commit()
    db.refresh(new_simulation_instance)

    logging.info(
        f"Created simulation instance with id {new_simulation_instance.id}."
    )
    return new_simulation_instance


def create_child_simulation(
    db: Session, root_simulation_id, simulation_type, duration_seconds,
    start_timestamp=None, end_timestamp=None
):
    # Create a new Child Simulation instance
    new_child_simulation_instance = models.ChildSimulationInstance(
        root_simulation=root_simulation_id,
        simulation_type=simulation_type,
        duration_seconds=duration_seconds
    )

    # Fill in non-mandatory fields
    if start_timestamp:
        new_child_simulation_instance.start_timestamp = start_timestamp
    if end_timestamp:
        new_child_simulation_instance.end_timestamp = end_timestamp

    db.add(new_child_simulation_instance)
    db.commit()
    db.refresh(new_child_simulation_instance)

    logging.info(
        "Created child simulation instance with id " +
        f"{new_child_simulation_instance.id}."
    )
    return new_child_simulation_instance


def create_simulation_ue(
    db: Session, simulation_id, phone_number, network_access_identifier,
    ipv4_address_public_address, ipv4_address_public_port,
    ipv4_address_private_address, ipv6_address
):
    # Create a new Simulation UE instance
    new_simulation_ue_instance = models.SimulationUE(
        simulation_instance=simulation_id,
        phone_number=phone_number,
        network_access_identifier=network_access_identifier,
        ipv4_address_public_address=ipv4_address_public_address,
        ipv4_address_public_port=ipv4_address_public_port,
        ipv4_address_private_address=ipv4_address_private_address,
        ipv6_address=ipv6_address
    )

    db.add(new_simulation_ue_instance)
    db.commit()
    db.refresh(new_simulation_ue_instance)

    logging.info(
        f"Created simulation UE with id {new_simulation_ue_instance.id}"
    )
    return new_simulation_ue_instance


def create_device_location_simulation_data_entry(
    db: Session, child_simulation_instance, simulation_instance, ue_id,
    latitude, longitude, timestamp
):
    # Create new device location entry in DB
    new_device_location_simulation_entry = models\
        .DeviceLocationSimulationData(
            child_simulation_instance=child_simulation_instance,
            simulation_instance=simulation_instance,
            ue=ue_id,
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp
        )

    db.add(new_device_location_simulation_entry)
    db.commit()
    db.refresh(new_device_location_simulation_entry)

    logging.info(
        "Created new device location simulation data entry for " +
        f"Simulation Instance {simulation_instance}, " +
        f"Child Simulation Instance {child_simulation_instance}: " +
        f"(ue_id: {new_device_location_simulation_entry.ue}, " +
        f"latitude: {new_device_location_simulation_entry.latitude}, " +
        f"longitude: {new_device_location_simulation_entry.longitude}, " +
        f"timestamp: {new_device_location_simulation_entry.timestamp})"
    )

    return new_device_location_simulation_entry


def try_to_update_simulation_end_timestamp(
    db: Session, simulation_id, end_timestamp
):
    # Get all child simulations
    child_simulations = db.query(models.ChildSimulationInstance).filter(
        models.ChildSimulationInstance.simulation_instance == simulation_id
    ).all()

    # Get all child simulations end timestamps
    end_timestamps = [
        child_sim.end_timestamp
        for child_sim
        in child_simulations
    ]

    # If all child simulations have ended, then we can also update the
    # root simulation end timestamp
    if None not in end_timestamps:
        db.query(models.SimulationInstance).filter(
            models.SimulationInstance.id == simulation_id
        ).update({models.SimulationInstance.end_timestamp: end_timestamp})
        db.commit()
        logging.info(
            f"End Timestamp ({end_timestamp}) updated in Simulation " +
            f"Instance {simulation_id}."
        )


def update_child_simulation_end_timestamp(
    db: Session, child_simulation_id, end_timestamp
):
    # First, update the child simulation end timestamp
    db.query(models.ChildSimulationInstance).filter(
        models.ChildSimulationInstance.id == child_simulation_id
    ).update({models.ChildSimulationInstance.end_timestamp: end_timestamp})
    db.commit()

    logging.info(
        f"End Timestamp ({end_timestamp}) updated in Child Simulation " +
        f"Instance {child_simulation_id}."
    )

    # Now, check if we can update the root simulation end timestamp
    root_simulation = get_simulation_instance_from_child(
        db, child_simulation_id
    )
    try_to_update_simulation_end_timestamp(
        db, root_simulation.id, end_timestamp
    )


def update_child_simulation_start_timestamp(
    db: Session, child_simulation_id, start_timestamp
):
    # First, update the child simulation start timestamp
    db.query(models.ChildSimulationInstance).filter(
        models.ChildSimulationInstance.id == child_simulation_id
    ).update({models.ChildSimulationInstance.start_timestamp: start_timestamp})
    db.commit()

    logging.info(
        f"Start Timestamp ({start_timestamp}) updated in Child Simulation " +
        f"Instance {child_simulation_id}."
    )

    # Now, check if root simulation already has a start_timestamp
    simulation_instance = get_simulation_instance_from_child(
        db, child_simulation_id
    )

    if not simulation_instance.start_timestamp:
        update_simulation_start_timestamp(
            db, simulation_instance.id, start_timestamp
        )


def update_simulation_start_timestamp(
    db: Session, simulation_id, start_timestamp
):
    # Update the simulation instance start timestamp
    db.query(models.SimulationInstance).filter(
            models.SimulationInstance.id == simulation_id
        ).update({models.SimulationInstance.start_timestamp: start_timestamp})

    db.commit()
    logging.info(
        f"Start Timestamp ({start_timestamp}) updated in Simulation " +
        f"Instance {simulation_id}."
    )


def get_simulation_instance_from_child(
    db: Session, child_simulation_id
):
    return db.query(models.SimulationInstance).filter(
        models.SimulationInstance.id == (
            db.query(models.ChildSimulationInstance)
            .filter(models.ChildSimulationInstance.id == child_simulation_id)
            .first().simulation_instance
        )
    ).first()


def simulation_can_start(
    db: Session, simulation: models.Simulation = None, simulation_id=None
):
    if not simulation_id:
        simulation_id = simulation.id

    # Verify if there are any simulation instances
    last_simulation_instance = db.query(models.SimulationInstance).filter(
        models.SimulationInstance.root_simulation == simulation_id
    ).order_by(models.SimulationInstance.id.desc()).first()

    # If there are no simulation instances, then this simulation was never
    # started before. Therefore, it can be started
    if not last_simulation_instance:
        logging.info(
            f"The simulation with id {simulation_id} was never started " +
            "before. Thus, it may be started."
        )
        return True

    # If there are simulation instances, then this simulation was started
    # before. We have to verify if there is any simulation instance running

    # If the simulation has an end_timestamp, then it can be started
    if last_simulation_instance.end_timestamp:
        logging.info(
            f"The last instance of the simulation with id {simulation_id} " +
            f"finished at {last_simulation_instance.end_timestamp}. Thus, " +
            f"the simulation with id {simulation_id} may be started."
        )
        return True
    # If there is no end_timestamp, we have to verify if the simulation was
    # already started before
    else:
        if not last_simulation_instance.start_timestamp:
            logging.info(
                f"The simulation with id {simulation_id} was never started " +
                "before. Thus, it may be started."
            )
            return True

    # If this function has not returned yet, it is because there is a
    # simulation running
    logging.info(
            f"There's an instance of the simulation with id {simulation_id}" +
            " running. Thus, one cannot start another simulation instance. " +
            f"The simulation with id {simulation_id} must be stopped first."
        )

    return False


def simulation_can_stop(
    db: Session, simulation: models.Simulation = None, simulation_id=None
):
    # If a simulation can be started, then it cannot be stopped, since it is
    # already stopped.
    # If a simulation cannot be started, then it can be stopped, since it is
    # running
    return not simulation_can_start(
        db=db,
        simulation=simulation,
        simulation_id=simulation_id
    )


def simulation_is_running(
    db: Session, simulation: models.Simulation = None, simulation_id=None
):
    # If simulation is running, then it can be stopped
    return simulation_can_stop(
        db=db,
        simulation=simulation,
        simulation_id=simulation_id
    )


def create_simulation_entities_required_for_starting_simulation(
    db: Session, simulation: models.Simulation
):
    # Create dict to store the entities created by this function
    created_entities = {
        "simulation_instance": None,
        "simulated_ues": [],
        "child_simulations": []
    }

    # Get the payload
    simulation_payload = json.loads(json.loads(simulation.payload))

    # These transactions must occur in a all vs nothing approach. Thus, it is
    # needed to create a savepoint
    db.begin_nested()

    try:
        # Create Simulation Instance
        new_simulation_instance = models.SimulationInstance(
            root_simulation=simulation.id,
            duration_seconds=simulation.duration_seconds,
            end_timestamp=None,
            start_timestamp=None
        )

        db.add(new_simulation_instance)
        db.flush()

        logging.info(
            "Created Simulation Instance with id " +
            f"{new_simulation_instance.id},  for Root Simulation with id " +
            f"{simulation.id}."
        )

        created_entities["simulation_instance"] = new_simulation_instance

        # Process the Simulation Devices
        for device in simulation_payload["devices"]:
            if not device.get("ipv4_address"):
                ipv4_address_public_address = ipv4_address_public_port = \
                    ipv4_address_private_address = None
            else:
                ipv4_address_public_address = device["ipv4_address"].get(
                    "public_address"
                )
                ipv4_address_public_port = device["ipv4_address"].get(
                    "public_port"
                )
                ipv4_address_private_address = device["ipv4_address"].get(
                    "private_address"
                )

            new_simulation_ue_instance = models.SimulationUE(
                simulation_instance=new_simulation_instance.id,
                phone_number=device.get("phone_number"),
                network_access_identifier=device.get(
                    "network_access_identifier"),
                ipv4_address_public_address=ipv4_address_public_address,
                ipv4_address_public_port=ipv4_address_public_port,
                ipv4_address_private_address=ipv4_address_private_address,
                ipv6_address=device.get("ipv6_address")
            )

            db.add(new_simulation_ue_instance)
            db.flush()

            logging.info(
                "Created Simulated UE with id " +
                f"{new_simulation_ue_instance.id}."
            )

            created_entities["simulated_ues"].append(
                new_simulation_ue_instance
            )

        # Process the child simulations
        for child_simulation in simulation_payload["child_simulations"]:
            if child_simulation["simulation_type"] == \
                    SimulationType.DEVICE_LOCATION.value:

                # Create a new Child Simulation instance
                new_child_simulation_instance = models.ChildSimulationInstance(
                    simulation_instance=new_simulation_instance.id,
                    simulation_type=child_simulation["simulation_type"],
                    duration_seconds=child_simulation["duration"]
                )

                db.add(new_child_simulation_instance)
                db.flush()

                logging.info(
                    "Created Child Simulation instance with id " +
                    f"{new_child_simulation_instance.id} for Root " +
                    f"Simulation with id {simulation.id}"
                )

                created_entities["child_simulations"].append(
                    new_child_simulation_instance
                )

        # Commit the transaction
        db.commit()
        return created_entities

    except Exception as e:
        logging.error(
            "Failed to create simulation entities required for starting the" +
            f"simulation {simulation.id}. Reason: {e}.\n Rolling back..."
        )
        db.rollback()
        logging.error("Rollback completed.")
        return None


def get_last_simulation_instance_from_root_simulation(
    db: Session, root_simulation_id
):
    return db.query(models.SimulationInstance).filter(
        models.SimulationInstance.root_simulation == (
            db.query(models.Simulation)
            .filter(models.Simulation.id == root_simulation_id)
        ).first().id
    ).order_by(models.SimulationInstance.id.desc()).first()


def get_last_child_simulation_instance_from_root_simulation(
    db: Session, root_simulation_id
):
    return db.query(models.ChildSimulationInstance).filter(
        models.ChildSimulationInstance.simulation_instance == (
            db.query(models.SimulationInstance).filter(
                models.SimulationInstance.root_simulation == (
                    db.query(models.Simulation)
                    .filter(models.Simulation.id == root_simulation_id)
                ).first().id
            ).order_by(models.SimulationInstance.id.desc()).first()
        ).id
    ).all()


def get_simulated_device_from_root_simulation(
    db: Session, root_simulation_id, device
):
    simulation_instance = get_last_simulation_instance_from_root_simulation(
        db=db,
        root_simulation_id=root_simulation_id
    )
    return db.query(models.SimulationUE).filter(
        models.SimulationUE.simulation_instance == simulation_instance.id,
        models.SimulationUE.phone_number == device.phone_number
    ).first()


def get_device_location_simulation_data(
    db: Session, root_simulation_id, ue: models.SimulationUE = None,
    ue_id: int = None
):
    if not ue_id:
        ue_id = ue.id

    simulation_instance = get_last_simulation_instance_from_root_simulation(
        db=db,
        root_simulation_id=root_simulation_id
    )

    return db.query(models.DeviceLocationSimulationData).filter(
        models.DeviceLocationSimulationData.simulation_instance ==
        simulation_instance.id,
        models.DeviceLocationSimulationData.ue == ue_id
    ).order_by(
        models.DeviceLocationSimulationData.id.desc()
    ).first()
