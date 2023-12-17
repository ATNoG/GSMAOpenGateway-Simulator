# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-12-12 13:39:13
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-12-12 14:27:38
import uvicorn
from multiprocessing import Process


class App:
    ...


app = App()


def run_app(app_name, port):
    uvicorn.run(f"main:{app_name}", reload=False, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    # Specify different ports for each instance
    port_1 = 8000
    port_2 = 8001
    app_1 = "app"
    app_2 = "app2"

    # Create separate processes for each instance
    process1 = Process(target=run_app, args=(app_1, port_1,))
    #process2 = Process(target=run_app, args=(app_2, port_2, ))

    # Start the processes
    process1.start()
    #process2.start()

    # Wait for both processes to finish
    process1.join()
    #process2.join()