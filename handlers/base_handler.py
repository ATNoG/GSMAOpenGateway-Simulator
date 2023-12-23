# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-22 11:23:39

class Handler():

    stop_handler = False

    def __init__(
        self, simulation_id, simulation_instance_id,
        child_simulation_instance_id
    ):
        self.simulation_id = simulation_id
        self.simulation_instance_id = simulation_instance_id
        self.child_simulation_instance_id = child_simulation_instance_id

    def process_message(self):
        # This method will be overwritten by the child classes
        pass
