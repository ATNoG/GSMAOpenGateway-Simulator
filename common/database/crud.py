# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-08 17:51:02
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 11:32:57

from sqlalchemy.orm import Session
from common.database import models
from common.simulation.simulation_types import SimulationType
import logging
import json
from common.apis.device_location_schemas import (
    CreateSubscription as DeviceLocationCreateSubscription
)
from common.apis.device_status_schemas import (
    CreateSubscription as DeviceStatusCreateSubscription
)
from datetime import datetime
import copy
from sqlalchemy import or_


def create_simulation(
    db: Session, name, description, duration_seconds, devices, mec_platforms,
    payload
):
    db.begin_nested()

    try:
        # Create a new Simulation instance
        new_simulation = models.Simulation(
            name=name,
            description=description,
            duration_seconds=duration_seconds,
            payload=payload
        )

        db.add(new_simulation)
        db.flush()
        db.refresh(new_simulation)

        logging.info(
            f"Created simulation with id {new_simulation.id}."
        )

        # Process the Simulation Devices
        for device in devices:
            if not device.ipv4_address:
                ipv4_address_public_address = ipv4_address_public_port = \
                    ipv4_address_private_address = None
            else:
                ipv4_address_public_address = device.ipv4_address\
                    .public_address
                ipv4_address_public_port = device.ipv4_address\
                    .public_port
                ipv4_address_private_address = device.ipv4_address\
                    .private_address

            new_simulation_ue = models.SimulationUE(
                root_simulation=new_simulation.id,
                phone_number=device.phone_number,
                network_access_identifier=device.network_access_identifier,
                ipv4_address_public_address=ipv4_address_public_address,
                ipv4_address_public_port=ipv4_address_public_port,
                ipv4_address_private_address=ipv4_address_private_address,
                ipv6_address=device.ipv6_address
            )

            db.add(new_simulation_ue)
            db.flush()

            logging.info(
                "Created Simulated UE with id " +
                f"{new_simulation_ue.id}."
            )

        # Process the Mec Platforms
        for mec_platform in mec_platforms:
            new_mec_platform = models.SimulationMecPlatform(
                root_simulation=new_simulation.id,
                edge_cloud_provider=mec_platform.edge_cloud_provider,
                edge_resource_name=mec_platform.edge_resource_name,
                latitude=mec_platform.latitude,
                longitude=mec_platform.longitude
            )

            db.add(new_mec_platform)
            db.flush()

            logging.info(
                "Created Mec Platform with id " +
                f"{new_mec_platform.id}."
            )

        # Commit the transaction
        db.commit()
        return new_simulation

    except Exception as e:
        logging.error(
            "Failed to create simulation entities for " +
            f"simulation {new_simulation.id}. Reason: {e}.\n Rolling back..."
        )
        db.rollback()
        logging.error("Rollback completed.")
        return None


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

    # Create dict to map the devices
    devices_mapping = {}

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

            simulation_ue = get_simulated_device_based_on_phone_number(
                db=db,
                root_simulation_id=simulation.id,
                phone_number=device.get("phone_number")
            )

            new_simulation_ue_instance = models.SimulationUEInstance(
                simulation_instance=new_simulation_instance.id,
                simulation_ue=simulation_ue.id
            )

            db.add(new_simulation_ue_instance)
            db.flush()

            # Update some fields in the simulated ue instances (but only
            # on the local object)
            new_simulation_ue_instance.phone_number = simulation_ue\
                .phone_number
            new_simulation_ue_instance.network_access_identifier = \
                simulation_ue.network_access_identifier
            new_simulation_ue_instance.ipv4_address_public_address = \
                simulation_ue.ipv4_address_public_address
            new_simulation_ue_instance.ipv4_address_private_address = \
                simulation_ue.ipv4_address_private_address
            new_simulation_ue_instance.ipv4_address_public_port = \
                simulation_ue.ipv4_address_public_port
            new_simulation_ue_instance.ipv6_address = \
                simulation_ue.ipv6_address

            logging.info(
                "Created Simulated UE with id " +
                f"{new_simulation_ue_instance.id}."
            )

            created_entities["simulated_ues"].append(
                new_simulation_ue_instance
            )

            devices_mapping[device["id"]] = new_simulation_ue_instance

        # Process the child simulations
        for child_simulation in simulation_payload["child_simulations"]:

            if child_simulation["simulation_type"] == \
                    SimulationType.DEVICE_LOCATION.value:

                initial_location = child_simulation["itinerary"][0]

                for device in child_simulation["devices"]:

                    # Create a new Child Simulation instance
                    new_child_simulation_instance = models\
                        .ChildSimulationInstance(
                            simulation_instance=new_simulation_instance.id,
                            simulation_type=child_simulation.get(
                                "simulation_type"
                            ),
                            duration_seconds=child_simulation.get(
                                "duration"
                            )
                        )

                    db.add(new_child_simulation_instance)
                    db.flush()

                    logging.info(
                        "Created Child Simulation instance (Type: " +
                        "DEVICE_LOCATION) with id " +
                        f"{new_child_simulation_instance.id} for Root " +
                        f"Simulation with id {simulation.id}"
                    )

                    # Add the initial location
                    simulation_entry = models\
                        .DeviceLocationSimulationData(
                            child_simulation_instance= # noqa
                            new_child_simulation_instance.id,
                            simulation_instance=new_simulation_instance.id,
                            ue=devices_mapping[device].id,
                            latitude=initial_location["latitude"],
                            longitude=initial_location["longitude"],
                            timestamp=datetime.utcnow(),
                        )

                    db.add(simulation_entry)
                    db.flush()

                    logging.info(
                        "Created new device location simulation data entry " +
                        "for Simulation Instance " +
                        f"{simulation_entry.simulation_instance}, "
                        "Child Simulation Instance " +
                        f"{simulation_entry.child_simulation_instance}: " +
                        f"(ue_id: {simulation_entry.ue}, " +
                        f"latitude: {simulation_entry.latitude}, " +
                        f"longitude: {simulation_entry.longitude}, " +
                        f"timestamp: {simulation_entry.timestamp})"
                    )

                    child_simulation["devices"] = [device]
                    created_entities["child_simulations"].append(
                        (
                            copy.deepcopy(new_child_simulation_instance),
                            copy.deepcopy(child_simulation)
                        )
                    )

            elif child_simulation["simulation_type"] == \
                    SimulationType.SIM_SWAP.value:

                for device in child_simulation["devices"]:
                    # Create a new Child Simulation instance
                    new_child_simulation_instance = models\
                        .ChildSimulationInstance(
                            simulation_instance=new_simulation_instance.id,
                            simulation_type=child_simulation.get(
                                "simulation_type"
                            ),
                            duration_seconds=max(
                                child_simulation.get(
                                    "timestamps_for_swaps_seconds"
                                )
                            )
                        )

                    db.add(new_child_simulation_instance)
                    db.flush()

                    logging.info(
                        "Created Child Simulation instance (Type: SIM_SWAP) " +
                        f"with id  {new_child_simulation_instance.id} for " +
                        f"Root Simulation with id {simulation.id}"
                    )

                    # Create new device location entry in DB
                    sim_swap_entry = models\
                        .SimSwapSimulationData(
                            child_simulation_instance= # noqa
                            new_child_simulation_instance.id,
                            simulation_instance=new_simulation_instance.id,
                            ue=devices_mapping[device].id,
                            new_msisdn="initial_msisdn",
                            timestamp=datetime.utcnow()
                        )

                    db.add(sim_swap_entry)
                    db.flush()

                    logging.info(
                        "Created new initial Swap simulation data entry for " +
                        f"Simulation Instance "
                        f"{sim_swap_entry.simulation_instance}, " +
                        f"Child Simulation Instance "
                        f"{sim_swap_entry.child_simulation_instance}: " +
                        f"(ue_id: {sim_swap_entry.ue}, " +
                        f"new_new_msisdn: {sim_swap_entry.new_msisdn}, " +
                        f"timestamp: {sim_swap_entry.timestamp})"
                    )

                    child_simulation["devices"] = [device]
                    created_entities["child_simulations"].append(
                        (
                            copy.deepcopy(new_child_simulation_instance),
                            copy.deepcopy(child_simulation)
                        )
                    )

            elif child_simulation["simulation_type"] == \
                    SimulationType.DEVICE_STATUS.value:

                initial_status = child_simulation["initial_device_status"]

                for device in child_simulation["devices"]:
                    # Get Max duration
                    duration = 0
                    for device_status_update in child_simulation.get(
                        "device_status_updates"
                    ):
                        if device_status_update["on_timestamp"] > duration:
                            duration = int(
                                device_status_update["on_timestamp"]
                            )

                    # Create a new Child Simulation instance
                    new_child_simulation_instance = models\
                        .ChildSimulationInstance(
                            simulation_instance=new_simulation_instance.id,
                            simulation_type=child_simulation.get(
                                "simulation_type"
                            ),
                            duration_seconds=duration
                        )

                    db.add(new_child_simulation_instance)
                    db.flush()

                    logging.info(
                        "Created Child Simulation instance " +
                        "(Type: DEVICE_STATUS) with id " +
                        f"{new_child_simulation_instance.id} for "
                        f"Root Simulation with id {simulation.id}"
                    )

                    # Create new device status entry in DB
                    device_status_entry = models\
                        .DeviceStatusSimulationData(
                            child_simulation_instance= # noqa
                            new_child_simulation_instance.id,
                            simulation_instance=new_simulation_instance.id,
                            ue=devices_mapping[device].id,
                            connectivity_status=initial_status[
                                "connectivity_status"
                            ],
                            roaming=initial_status[
                                "roaming"
                            ],
                            country_code=initial_status[
                                "country_code"
                            ],
                            country_name=json.dumps(
                                initial_status["country_name"]
                            )
                        )

                    db.add(device_status_entry)
                    db.flush()

                    logging.info(
                        "Created new initial Device Status data entry for " +
                        f"Simulation Instance "
                        f"{device_status_entry.simulation_instance}, " +
                        f"Child Simulation Instance "
                        f"{device_status_entry.child_simulation_instance}: " +
                        f"(ue_id: {device_status_entry.ue}, " +
                        "new_connectivity_status: " +
                        f"{device_status_entry.connectivity_status}, " +
                        f"roaming: {device_status_entry.roaming}, " +
                        "country_code: " +
                        f"{device_status_entry.country_code}, " +
                        "country_name: " +
                        f"{device_status_entry.country_name})"
                    )

                    child_simulation["devices"] = [device]
                    created_entities["child_simulations"].append(
                        (
                            copy.deepcopy(new_child_simulation_instance),
                            copy.deepcopy(child_simulation)
                        )
                    )

        # Commit the transaction
        db.commit()
        return created_entities

    except Exception as e:
        logging.error(
            "Failed to create simulation entities required for starting the " +
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


def get_child_simulation_instances_from_root_simulation(
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


def get_simulated_device_instance_from_root_simulation(
    db: Session, root_simulation_id, device
):
    simulation_instance = get_last_simulation_instance_from_root_simulation(
        db=db,
        root_simulation_id=root_simulation_id
    )

    simulation_ue = get_simulated_device_from_root_simulation(
        db=db,
        root_simulation_id=root_simulation_id,
        device=device
    )

    ue = db.query(models.SimulationUEInstance).filter(
        models.SimulationUEInstance.simulation_instance ==
        simulation_instance.id,
        models.SimulationUEInstance.simulation_ue == simulation_ue.id
    ).first()

    ue.phone_number = simulation_ue.phone_number
    ue.network_access_identifier = simulation_ue.network_access_identifier
    ue.ipv4_address_public_address = simulation_ue.ipv4_address_public_address
    ue.ipv4_address_private_address = \
        simulation_ue.ipv4_address_private_address
    ue.ipv4_address_public_port = simulation_ue.ipv4_address_public_port
    ue.ipv6_address = simulation_ue.ipv6_address

    return ue


def get_device_instance_based_on_simulated_ue(
    db: Session, root_simulation_id, simulated_ue_id
):
    simulation_instance = get_last_simulation_instance_from_root_simulation(
        db=db,
        root_simulation_id=root_simulation_id
    )

    simulated_ue = db.query(models.SimulationUE).filter(
        models.SimulationUE.root_simulation == root_simulation_id,
        models.SimulationUE.id == simulated_ue_id
    ).first()

    ue = db.query(models.SimulationUEInstance).filter(
        models.SimulationUEInstance.simulation_instance ==
        simulation_instance.id,
        models.SimulationUEInstance.simulation_ue == simulated_ue.id
    ).first()

    ue.phone_number = simulated_ue.phone_number
    ue.network_access_identifier = simulated_ue.network_access_identifier
    ue.ipv4_address_public_address = simulated_ue.ipv4_address_public_address
    ue.ipv4_address_private_address = \
        simulated_ue.ipv4_address_private_address
    ue.ipv4_address_public_port = simulated_ue.ipv4_address_public_port
    ue.ipv6_address = simulated_ue.ipv6_address

    return ue


def get_simulated_device_instance_from_root_simulation_via_phone_number(
    db: Session, root_simulation_id, device_phone_number
):
    simulation_instance = get_last_simulation_instance_from_root_simulation(
        db=db,
        root_simulation_id=root_simulation_id
    )

    simulation_ue = db.query(models.SimulationUE).filter(
        models.SimulationUE.root_simulation == root_simulation_id,
        models.SimulationUE.phone_number == device_phone_number
    ).first()

    if not simulation_ue:
        return None

    return db.query(models.SimulationUEInstance).filter(
        models.SimulationUEInstance.simulation_instance
        == simulation_instance.id,
        models.SimulationUEInstance.simulation_ue == simulation_ue.id
    ).first()


def get_simulated_device_from_root_simulation(
    db: Session, root_simulation_id, device
):
    return db.query(models.SimulationUE).filter(
        models.SimulationUE.root_simulation == root_simulation_id,
        models.SimulationUE.phone_number == device.phone_number
    ).first()


def get_simulated_device_based_on_phone_number(
    db: Session, root_simulation_id, phone_number
):
    return db.query(models.SimulationUE).filter(
        models.SimulationUE.root_simulation == root_simulation_id,
        models.SimulationUE.phone_number == phone_number
    ).first()


def get_simulated_device_based_on_several_parameters(
    db: Session, root_simulation_id, phone_number, network_access_identifier,
    ip_address
):
    # We assume that all the above listed attributes are UNIQUE.
    return db.query(models.SimulationUE).filter(
        models.SimulationUE.root_simulation == root_simulation_id,
        or_(
            models.SimulationUE.phone_number == phone_number,
            models.SimulationUE.ipv4_address_public_address == ip_address,
            models.SimulationUE.ipv6_address == ip_address,
            models.SimulationUE.network_access_identifier
            == network_access_identifier,
        )
    ).first()


def get_simulated_device_from_id(
    db: Session, device_id
):
    return db.query(models.SimulationUE).filter(
        models.SimulationUE.id == device_id,
    ).first()


def get_device_location_simulation_data(
    db: Session, root_simulation_id, ue: models.SimulationUEInstance = None,
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


def create_device_location_subscription(
    db: Session, root_simulation_id: int, ue_id: int,
    subscription: DeviceLocationCreateSubscription
):
    # Create a new Device Location Subscription
    new_device_location_subscription = models.DeviceLocationSubscription(
        root_simulation=root_simulation_id,
        ue=ue_id,
        area=json.dumps(
            subscription.subscription_detail.area.model_dump_json()
        ),
        subscription_type=subscription.subscription_detail.type.value,
        webhook_url=subscription.webhook.notification_url,
        webhook_auth_token=subscription.webhook.notification_auth_token,
        start_time=datetime.utcnow(),
        expire_time=subscription.subscription_expire_time
    )

    db.add(new_device_location_subscription)
    db.commit()
    db.refresh(new_device_location_subscription)

    logging.info(
        "Created subscription with id" +
        f"{new_device_location_subscription.id} (Root Simulation " +
        f"{root_simulation_id})."
    )
    return new_device_location_subscription


def get_device_location_subscriptions_for_root_simulation(
    db: Session, root_simulation_id: int
):
    return db.query(models.DeviceLocationSubscription).filter(
        models.DeviceLocationSubscription.root_simulation == root_simulation_id
    ).all()


def get_active_device_location_subscriptions_for_root_simulation(
    db: Session, root_simulation_id: int
):
    return db.query(models.DeviceLocationSubscription).filter(
        models.DeviceLocationSubscription.expire_time > datetime.utcnow(),
        models.DeviceLocationSubscription.root_simulation == root_simulation_id
    ).all()


def get_device_location_subscription_for_root_simulation(
    db: Session, root_simulation_id: int, subscription_id: int
):
    return db.query(models.DeviceLocationSubscription).filter(
        models.DeviceLocationSubscription.id == subscription_id,
        models.DeviceLocationSubscription.root_simulation == root_simulation_id
    ).first()


def delete_location_subscription(
    db: Session, subscription: models.DeviceLocationSubscription
):
    db.delete(subscription)
    db.commit()


def create_device_location_subscription_notification(
    db: Session, subscription_id: str, sucess: bool = None,
    error: str = None
):
    new_notification = models.DeviceLocationSubscriptionNotification(
        subscription_id=subscription_id,
    )

    if sucess:
        new_notification.sucess = sucess
    if error:
        new_notification.error = error

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


def update_device_location_subscription_notification(
    db: Session, notification_id: int, sucess: bool = None,
    error: str = None
):
    notification = db.query(
        models.DeviceLocationSubscriptionNotification
    ).filter(
        models.DeviceLocationSubscriptionNotification.id == notification_id,
    ).first()

    if sucess:
        notification.sucess = sucess
    if error:
        notification.error = error

    db.commit()
    db.refresh(notification)

    return notification


def get_simulated_device_id_from_simulated_device_instance(
    db: Session, simulated_device_instance_id: int
):
    return db.query(models.SimulationUEInstance).filter(
        models.SimulationUEInstance.id == simulated_device_instance_id,
    ).first().simulation_ue


def get_all_child_simulation_instances_running(db):
    return db.query(
            models.ChildSimulationInstance
        ).filter(
            models.ChildSimulationInstance.end_timestamp == None # noqa
    ).all()


def create_sim_swap_simulation_data_entry(
    db: Session, child_simulation_instance, simulation_instance, ue_id,
    new_msisdn, timestamp
):
    # Create new device location entry in DB
    new_sim_swap_simulation_entry = models\
        .SimSwapSimulationData(
            child_simulation_instance=child_simulation_instance,
            simulation_instance=simulation_instance,
            ue=ue_id,
            new_msisdn=new_msisdn,
            timestamp=timestamp
        )

    db.add(new_sim_swap_simulation_entry)
    db.commit()
    db.refresh(new_sim_swap_simulation_entry)

    logging.info(
        "Created new SIM Swap simulation data entry for " +
        f"Simulation Instance {simulation_instance}, " +
        f"Child Simulation Instance {child_simulation_instance}: " +
        f"(ue_id: {new_sim_swap_simulation_entry.ue}, " +
        f"new_new_msisdn: {new_sim_swap_simulation_entry.new_msisdn}, " +
        f"timestamp: {new_sim_swap_simulation_entry.timestamp})"
    )

    return new_sim_swap_simulation_entry


def get_sim_swap_simulation_data(
    db: Session, root_simulation_id, ue: models.SimulationUE = None,
    ue_id: int = None
):
    if not ue_id:
        ue_id = ue.id

    simulation_instance = get_last_simulation_instance_from_root_simulation(
        db=db,
        root_simulation_id=root_simulation_id
    )

    return db.query(models.SimSwapSimulationData).filter(
        models.SimSwapSimulationData.simulation_instance ==
        simulation_instance.id,
        models.SimSwapSimulationData.ue == ue_id
    ).order_by(
        models.SimSwapSimulationData.id.desc()
    ).first()


def get_mec_platforms_for_root_simulation(
    db: Session, root_simulation_id: int
):
    return db.query(models.SimulationMecPlatform).filter(
        models.SimulationMecPlatform.root_simulation == root_simulation_id
    ).all()


def create_device_status_simulation_data_entry(
    db: Session, child_simulation_instance, simulation_instance, ue_id,
    connectivity_status, roaming, country_code, country_name
):
    if not country_name:
        country_name = []

    # Create new device status entry in DB
    new_device_status_simulation_entry = models\
        .DeviceStatusSimulationData(
            child_simulation_instance=child_simulation_instance,
            simulation_instance=simulation_instance,
            ue=ue_id,
            connectivity_status=connectivity_status,
            roaming=roaming,
            country_code=country_code,
            country_name=json.dumps(country_name)
        )

    db.add(new_device_status_simulation_entry)
    db.commit()
    db.refresh(new_device_status_simulation_entry)

    logging.info(
        "Created new Device Status simulation data entry for " +
        f"Simulation Instance {simulation_instance}, " +
        f"Child Simulation Instance {child_simulation_instance}: " +
        f"(ue_id: {new_device_status_simulation_entry.ue}, " +
        "new_connectivity_status: " +
        f"{new_device_status_simulation_entry.connectivity_status}, " +
        f"roaming: {new_device_status_simulation_entry.roaming}, " +
        "country_code: " +
        f"{new_device_status_simulation_entry.country_code}, " +
        "country_name: " +
        f"{new_device_status_simulation_entry.country_name})"
    )

    return new_device_status_simulation_entry


def get_last_device_status_entry(
    db: Session, simulation_instance, ue_id
):
    # Query the database to find the most recent entry for the given parameters
    return db.query(models.DeviceStatusSimulationData)\
        .filter(
            models.DeviceStatusSimulationData.simulation_instance ==
            simulation_instance,
            models.DeviceStatusSimulationData.ue == ue_id
        ).order_by(
            models.DeviceStatusSimulationData.id.desc()
        ).first()


def create_device_status_subscription(
    db: Session, root_simulation_id: int, ue_id: int,
    subscription: DeviceStatusCreateSubscription
):
    # Create a new Device Location Subscription
    new_device_status_subscription = models.DeviceStatusSubscription(
        root_simulation=root_simulation_id,
        ue=ue_id,
        subscription_type=subscription.subscription_detail.type.value,
        webhook_url=subscription.webhook.notification_url,
        webhook_auth_token=subscription.webhook.notification_auth_token,
        start_time=datetime.utcnow(),
        expire_time=subscription.subscription_expire_time
    )

    db.add(new_device_status_subscription)
    db.commit()
    db.refresh(new_device_status_subscription)

    logging.info(
        "Created device status subscription with id" +
        f"{new_device_status_subscription.id} (Root Simulation " +
        f"{root_simulation_id})."
    )
    return new_device_status_subscription


def get_device_status_subscriptions_for_root_simulation(
    db: Session, root_simulation_id: int
):
    return db.query(models.DeviceStatusSubscription).filter(
        models.DeviceStatusSubscription.root_simulation == root_simulation_id
    ).all()


def get_active_device_status_subscriptions_for_root_simulation(
    db: Session, root_simulation_id: int
):
    return db.query(models.DeviceStatusSubscription).filter(
        models.DeviceStatusSubscription.expire_time > datetime.utcnow(),
        models.DeviceStatusSubscription.root_simulation == root_simulation_id
    ).all()


def get_device_status_subscription_for_root_simulation(
    db: Session, root_simulation_id: int, subscription_id: int
):
    return db.query(models.DeviceStatusSubscription).filter(
        models.DeviceStatusSubscription.id == subscription_id,
        models.DeviceStatusSubscription.root_simulation == root_simulation_id
    ).first()


def delete_device_status_subscription(
    db: Session, subscription: models.DeviceStatusSubscription
):
    db.delete(subscription)
    db.commit()


def create_device_status_subscription_notification(
    db: Session, subscription_id: str, sucess: bool = None,
    error: str = None
):
    new_notification = models.DeviceStatusSubscriptionNotification(
        subscription_id=subscription_id,
    )

    if sucess:
        new_notification.sucess = sucess
    if error:
        new_notification.error = error

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    return new_notification


def update_device_status_subscription_notification(
    db: Session, notification_id: int, sucess: bool = None,
    error: str = None
):
    notification = db.query(
        models.DeviceStatusSubscriptionNotification
    ).filter(
        models.DeviceStatusSubscriptionNotification.id == notification_id,
    ).first()

    if sucess:
        notification.sucess = sucess
    if error:
        notification.error = error

    db.commit()
    db.refresh(notification)

    return notification