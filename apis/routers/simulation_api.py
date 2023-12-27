# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 10:54:41
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-27 17:16:50
# coding: utf-8
from fastapi import APIRouter, Depends
import json
from sqlalchemy.orm import Session
import logging
import config # noqa
from common.apis import simulation_schemas as SimulationSchemas
from common.database import connections_factory as DBFactory
from common.database import crud
from helpers import simulations as SimulationHelpers
from helpers import message_broker as PikaHelper
from common.helpers import device_location as DeviceLocationHelpers
router = APIRouter()


@router.post(
    "",
    responses={
        # Todo: Add responses later
    },
    tags=["Simulation"],
    summary="Create new simulation",
    response_model_by_alias=True,
)
async def create_simulation(
    root_simulation: SimulationSchemas.RootSimulationCreate,
    db: Session = Depends(DBFactory.get_db_session)
) -> SimulationSchemas.RootSimulationCreateResponse:

    # Todo: Verify if the devices in the simulations were declared 
    # Todo: as simulation devices

    # Todo: Verify if the devices unique information is indeed unique
    # Todo: ips, cellphone numbers, etc

    # Todo: Verify if the same UE is not referenced in several simultaneous 
    # Todo: child simulations

    # Todo: Consider the other remaining simulations to account for the overall
    # Todo: simulation duration
    duration_seconds = max([
        child_simulation.duration
        for child_simulation
        in root_simulation.child_simulations
        if isinstance(
            child_simulation,
            SimulationSchemas.DeviceLocationSimulation
        )
    ])

    simulation = crud.create_simulation(
        db=db,
        name=root_simulation.name,
        description=root_simulation.description,
        duration_seconds=duration_seconds,
        devices=root_simulation.devices,
        payload=json.dumps(root_simulation.model_dump_json())
    )

    logging.debug(
        f"Simulation {simulation.id} Payload:\n" +
        f"{root_simulation.model_dump_json(indent=4)}"
    )

    response = SimulationSchemas.RootSimulationCreateResponse(
        id=simulation.id,
        duration_seconds=simulation.duration_seconds,
        name=simulation.name,
        description=simulation.description,
        devices=root_simulation.devices,
        child_simulations=root_simulation.child_simulations
    )

    return response


@router.get(
    "/{simulaton_id}",
    responses={
        # Todo: Add responses later
    },
    tags=["Simulation"],
    summary="Update a simulation",
    response_model_by_alias=True,
)
async def get_simulation(
    simulaton_id: int,
    db: Session = Depends(DBFactory.get_db_session)
) -> SimulationSchemas.RootSimulationCreateResponse:

    simulation = crud.get_simulation(
        db=db,
        simulation_id=simulaton_id
    )

    # Todo: What if the simulation does not exist?
    if not simulation:
        pass

    root_simulation_from_payload = SimulationSchemas.RootSimulationCreate(
        **json.loads(json.loads(simulation.payload))
    )

    # Parse Simulated Devices
    simulated_devices = DeviceLocationHelpers\
        .parse_payload_ues_to_simulated_ue_objects(
            json.loads(json.loads(simulation.payload))["devices"]
        )

    return SimulationSchemas.RootSimulationCreateResponse(
        id=simulation.id,
        duration_seconds=simulation.duration_seconds,
        name=simulation.name,
        description=simulation.description,
        devices=simulated_devices,
        child_simulations=root_simulation_from_payload.child_simulations
    )


@router.patch(
    "/{simulaton_id}",
    responses={
        # Todo: Add responses later
    },
    tags=["Simulation"],
    summary="Update a simulation",
    response_model_by_alias=True,
)
async def update_simulation(
    simulaton_id: int,
    db: Session = Depends(DBFactory.get_db_session)
) -> SimulationSchemas.RootSimulationCreateResponse:

    # Todo: Implement Later
    simulation = crud.get_simulation(
        db=db,
        simulation_id=simulaton_id
    )

    # Todo: What if the simulation does not exist?
    if not simulation:
        pass

    root_simulation_from_payload = SimulationSchemas.RootSimulationCreate(
        **json.loads(json.loads(simulation.payload))
    )

    return SimulationSchemas.RootSimulationCreateResponse(
        id=simulation.id,
        duration_seconds=simulation.duration_seconds,
        name=simulation.name,
        description=simulation.description,
        devices=root_simulation_from_payload.devices,
        child_simulations=root_simulation_from_payload.child_simulations
    )


@router.delete(
    "/{simulaton_id}",
    responses={
        # Todo: Add responses later
    },
    tags=["Simulation"],
    summary="Update a simulation",
    response_model_by_alias=True,
)
async def delete_simulation(
    simulaton_id: int,
    db: Session = Depends(DBFactory.get_db_session)
) -> SimulationSchemas.RootSimulationCreateResponse:

    # Todo: Implement Later
    simulation = crud.get_simulation(
        db=db,
        simulation_id=simulaton_id
    )

    # Todo: What if the simulation does not exist?
    if not simulation:
        pass

    # Todo: implement the deletion -> CASCADE DELETION

    root_simulation_from_payload = SimulationSchemas.RootSimulationCreate(
        **json.loads(json.loads(simulation.payload))
    )

    return SimulationSchemas.RootSimulationCreateResponse(
        id=simulation.id,
        duration_seconds=simulation.duration_seconds,
        name=simulation.name,
        description=simulation.description,
        devices=root_simulation_from_payload.devices,
        child_simulations=root_simulation_from_payload.child_simulations
    )


@router.post(
    "/{simulation_id}/start",
    responses={
        # Todo: Add responses later
    },
    tags=["Simulation"],
    summary="Create new simulation",
    response_model_by_alias=True,
)
async def start_simulation(
    simulation_id: int,
    db: Session = Depends(DBFactory.get_db_session)
) -> bool:

    simulation = crud.get_simulation(
        db=db,
        simulation_id=simulation_id
    )

    # Todo: What if the simulation does not exist?
    if not simulation:
        return False

    # If the simulation can start, delegate to the simulations business logic
    # module
    # Todo: Since we use the start timestamp to check if the simulation is
    # Todo: running and the TS will be updated by the simulation threads,
    # Todo: what happens if a simulation was started, but the sim. threads have
    # Todo: not update the TS and the user triggers a new start?
    # Todo: With the the current code, it will be possible to start another
    # Todo: simulation instance -> THIS IS WRONG AND MUST BE UPDATED
    if crud.simulation_can_start(db=db, simulation=simulation):
        created_entities = crud \
            .create_simulation_entities_required_for_starting_simulation(
                db=db,
                simulation=simulation
            )

        # If the entities creation failed...
        if isinstance(created_entities, Exception):
            # Todo: Pass the exception to the client's response
            return False

        # Get UES from DB and update the payload
        simulation_payload = json.loads(json.loads(simulation.payload))

        SimulationHelpers\
            .update_simulation_payload_with_correct_device_ids(
                simulation_payload=simulation_payload,
                simulated_ues=created_entities["simulated_ues"],
                child_simulations=created_entities["child_simulations"]
            )

        # Create the pika message to trigger the simulation
        simulation_start_messages = SimulationHelpers\
            .compose_simulation_start_messages_for_child_simulations(
                simulation.id,
                created_entities["simulation_instance"],
                created_entities["child_simulations"]
            )

        PikaHelper.send_simulation_messages(simulation_start_messages)
    else:
        # Todo: Inform the client that the simulation cannot be started
        return False

    return True


@router.post(
    "/{simulation_id}/stop",
    responses={
        # Todo: Add responses later
    },
    tags=["Simulation"],
    summary="Stop Running Simulation",
    response_model_by_alias=True,
)
async def stop_simulation(
    simulation_id: int,
    db: Session = Depends(DBFactory.get_db_session)
) -> bool:

    simulation = crud.get_simulation(
        db=db,
        simulation_id=simulation_id
    )

    # Todo: What if the simulation does not exist?
    if not simulation:
        return False

    # If the simulation can stop, delegate to the simulations business logic
    # module
    if crud.simulation_can_stop(db=db, simulation=simulation):

        # Get the last child simulation instances. These are the ones that must
        # be stopped
        child_simulation_instances = crud\
            .get_child_simulation_instances_from_root_simulation(
                db=db,
                root_simulation_id=simulation.id
            )

        # Create the pika message to trigger the simulation
        simulation_stop_messages = SimulationHelpers\
            .compose_simulation_stop_messages_for_child_simulations(
                simulation.id,
                child_simulation_instances
            )

        PikaHelper.send_simulation_messages(simulation_stop_messages)
    else:
        # Todo: Inform the client that the simulation cannot be stopped
        return False

    return True


@router.post(
    "/{simulaton_id}/status",
    responses={
        # Todo: Add responses later
    },
    tags=["Simulation"],
    summary="Get Simulation Running Status",
    response_model_by_alias=True,
)
async def simulation_status(
    simulaton_id: int,
    db: Session = Depends(DBFactory.get_db_session)
) -> str:

    simulation = crud.get_simulation(
        db=db,
        simulation_id=simulaton_id
    )

    # Todo: What if the simulation does not exist?
    if not simulation:
        return "SIMULATION_NOT_FOUND"

    # If the simulation can stop, delegate to the simulations business logic
    # module
    if crud.simulation_is_running(db=db, simulation=simulation):
        return "RUNNING"
    else:
        return "NOT RUNNING"
