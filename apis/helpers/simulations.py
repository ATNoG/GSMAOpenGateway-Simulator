# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-13 10:52:05
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 11:07:38

import config # noqa
from common.message_broker import schemas as SimulationMessageSchemas


def update_simulation_payload_with_correct_device_ids(
    simulation_payload, simulated_ues
):
    # index the simulated UES by phone_number
    indexed_simulated_ues = {
        simulated_ue.phone_number: simulated_ue
        for simulated_ue
        in simulated_ues
    }

    # index the payload UES by their ids
    indexed_payload_ues = {
        ue["id"]: ue
        for ue
        in simulation_payload["devices"]
    }

    for child_simulation in simulation_payload["child_simulations"]:
        # get the simulation ues
        for i in range(len(child_simulation["devices"])):
            child_simulation["devices"][i] = indexed_simulated_ues.get(
                indexed_payload_ues.get(
                    child_simulation["devices"][i]
                ).get(
                    "phone_number"
                )
            ).id


def compose_simulation_start_messages_for_child_simulations(
    simulation_id, simulation_instance, child_simulation_instances,
    simulation_payload
):
    assert len(simulation_payload["child_simulations"]) == len(
        child_simulation_instances)

    simulation_start_messages = []

    for i in range(len(child_simulation_instances)):
        simulation_start_messages.append(
            SimulationMessageSchemas.SimulationAction(
                simulation_id=simulation_id,
                action=SimulationMessageSchemas.SimulationOperation.START,
                simulation_type=child_simulation_instances[i].simulation_type,
                simulation_instance_id=simulation_instance.id,
                child_simulation_instance_id=child_simulation_instances[i].id,
                simulation_config=simulation_payload["child_simulations"][i]
            )
        )

    return simulation_start_messages


def compose_simulation_stop_messages_for_child_simulations(
    simulation_id, child_simulation_instances
):
    return [
        SimulationMessageSchemas.SimulationAction(
            simulation_id=simulation_id,
            action=SimulationMessageSchemas.SimulationOperation.STOP,
            simulation_type=child_simulation_instance.simulation_type,
            simulation_instance_id=child_simulation_instance
            .simulation_instance,
            child_simulation_instance_id=child_simulation_instance.id
        )
        for child_simulation_instance
        in child_simulation_instances
    ]
