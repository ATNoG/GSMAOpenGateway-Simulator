# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-06 22:11:26
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-11 20:50:30

class Handler():

    stop_handler = False

    def __init__(self, simulation_id, child_simulation_id):
        self.simulation_id = simulation_id
        self.child_simulation_id = child_simulation_id

    def process_message(self):
        # This method will be overwritten by the child classes
        pass
