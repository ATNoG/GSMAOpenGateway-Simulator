# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2024-01-11 14:37:36
import networkx
import osmnx as ox
import threading
import config # noqa
from aux.ue_movement import UEMovement
from base_simulation import Simulation
from common.simulation.simulation_types import SimulationType
from common.message_broker import connections_factory as PikaFactory
from common.message_broker import schemas as SimulationSchemas
from common.database import crud
from common.message_broker.topics import Topics

ox.config(use_cache=True, log_console=True)


class DeviceLocationSimulation(Simulation):

    ue_threads = []
    moving_ues = []
    moving_ues_count = None
    simulation_type = SimulationType.DEVICE_LOCATION

    def __init__(
        self, db, simulation_id, simulation_instance_id, child_simulation_id,
        simulation_payload
    ):
        # Load location graph
        self.graph = ox.io.load_graphml('aveiro.graphml')
        # Initialize super
        super().__init__(
            db, simulation_id, simulation_instance_id, child_simulation_id,
            simulation_payload
        )

    def create_itinerary(self, stops, graph):

        gdf_nodes = ox.graph_to_gdfs(graph)[0]
        all_path_nodes = []
        all_path_coord = []

        # For every location in the route create an entry with a location_id, a
        # start location and a path list from start to location
        for i in range(1, len(stops)):
            # Set Start and End
            y1, x1 = [stops[i-1]["latitude"], stops[i-1]["longitude"]]
            y2, x2 = [stops[i]["latitude"], stops[i]["longitude"]]

            # Compute the nodes in the path as well as their coordinates
            nodes = ox.nearest_nodes(G=graph, X=[x1, x2], Y=[y1, y2])
            path_nodes = networkx.shortest_path(graph, nodes[0], nodes[1])
            path_coord = gdf_nodes.loc[path_nodes][['x', 'y']]

            # save
            all_path_nodes += path_nodes
            all_path_coord += path_coord.values.tolist()

        return list(zip(all_path_nodes, all_path_coord))

    def compute_itineraries(self):

        for ue_instance in self.simulation_payload["devices"]:

            # Get Root UE
            ue = crud.get_simulated_device_id_from_simulated_device_instance(
                db=self.db,
                simulated_device_instance_id=ue_instance
            )

            self.itineraries.append(
                (
                    ue,
                    ue_instance,
                    self.simulation_payload["duration"],
                    self.create_itinerary(
                        stops=self.simulation_payload["itinerary"],
                        graph=self.graph
                    )
                )
            )

    def signal_that_ue_has_stopped(self):
        self.moving_ues_count -= 1
        if self.moving_ues_count == 0:
            # Inform Events Module that the Simulation has ended
            self.inform_events_module_that_simulation_has_ended()
            # Signal that the simulation has ended
            self.signal_that_simulation_ended()

    def start_simulation(self):

        # create itineraries
        self.itineraries = []
        self.moving_ues = []
        self.compute_itineraries()

        # Start the simulation
        # The super start_simulation will handle everything that is common to
        # all types of simulations - e.g., updating the simulation's
        # start_timestamp
        super().start_simulation()

        for ue, ue_instance, duration, itinerary in self.itineraries:
            connection, channel = PikaFactory\
                .get_new_pika_connection_and_channel()
            self.moving_ues.append(
                UEMovement(
                    simulation=self,
                    ue=ue,
                    ue_instance=ue_instance,
                    itinerary=itinerary,
                    simulation_duration=duration,
                    message_queue_channel=channel,
                    message_queue_connection=connection
                )
            )

        # Todo: Using threads is far from being the best approach to deal 
        # Todo: with this
        # Todo: This threading appraoch must be replaced by a more resilient 
        # Todo: one

        # Create threads
        self.ue_threads = [
            threading.Thread(target=ue.move)
            for ue
            in self.moving_ues
        ]
        self.moving_ues_count = len(self.ue_threads)

        # Start the threads
        for thread in self.ue_threads:
            thread.start()

    def stop_simulation(self):
        # Stop all moving UEs
        for moving_ue in self.moving_ues:
            moving_ue.stop()
        # Wait for all threads to finish
        for thread in self.ue_threads:
            thread.join()

        # Inform Events Module that the Simulation has ended
        self.inform_events_module_that_simulation_has_ended()

        # Signal that the simulation has ended
        self.signal_that_simulation_ended()

    def inform_events_module_that_simulation_has_ended(self):
        simulation_data = SimulationSchemas.SimulationData(
            simulation_id=self.simulation_id,
            simulation_instance_id=self.simulation_instance_id,
            child_simulation_instance_id=self.child_simulation_id,
            simulation_type=self.simulation_type,
            data=SimulationSchemas.DeviceLocationSimulationData(
                stop=True,
                ue=-1,
                ue_instance=-1,
                latitude=-1,
                longitude=-1,
                timestamp=""
            )
        )

        _, channel = PikaFactory\
            .get_new_pika_connection_and_channel()

        channel.basic_publish(
            exchange='',
            routing_key=Topics.EVENTS.value,
            body=simulation_data.model_dump_json()
        )

        channel.close()
