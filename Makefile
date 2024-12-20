SHELL := /bin/bash

# Function to determine Docker Compose command
define docker_compose_cmd
	$(if $(shell command -v docker compose 2> /dev/null),docker compose,$(if $(shell command -v docker-compose 2> /dev/null),docker-compose,))
endef

# RabbitMQ 
start_rabbit:
	$(call docker_compose_cmd) up -d

stop_rabbit:
	$(call docker_compose_cmd) down

# Requirements
install_dependencies:
	python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

delete_dependencies:
	rm -rf venv

# Simulations Orchestrator
run_simulations_orchestrator:
	source venv/bin/activate && python simulations/simulations_orchestrator.py

# Simulations Handler
run_simulations_handler:
	source venv/bin/activate && python handlers/handlers_orchestrator.py

# Simulations Events Orchestrator
run_events_orchestrator:
	source venv/bin/activate && python events/events_orchestrator.py

# Simulations API
run_simulations_api:
	source venv/bin/activate && \
	cd apis && \
    echo -e "\nLaunching FastAPI server for the Simulations API...\n" && \
    uvicorn main:simulation_app --reload --port 8000

# Device Location Retrieval API
run_device_location_retrieval_api:
	source venv/bin/activate && \
	cd apis && \
    echo -e "\nLaunching FastAPI server for the Device Location Retrieval API...\n" && \
    uvicorn main:device_location_retrieval_app --reload --port 8001 

# Device Location Verification API
run_device_location_verification_api:
	source venv/bin/activate && \
	cd apis && \
     echo -e "\nLaunching FastAPI server for the Device Location Vertification API...\n" && \
    uvicorn main:device_location_verification_app --reload --port 8002

# Device Location Geofencing API
run_device_location_geofencing_api:
	source venv/bin/activate && \
	cd apis && \
     echo -e "\nLaunching FastAPI server for the Device Location Geofencing API...\n" && \
    uvicorn main:device_location_geofencing_app --reload --port 8003

# SIM Swap API
run_sim_swap_api:
	source venv/bin/activate && \
	cd apis && \
    echo -e "\nLaunching FastAPI server for the SIM Swap API...\n" && \
    uvicorn main:sim_swap_app --reload --port 8004

# Simple Edge Discovery API
run_simple_edge_discovery_api:
	source venv/bin/activate && \
	cd apis && \
    echo -e "\nLaunching FastAPI server for the Simple Edge Discovery API...\n" && \
    uvicorn main:simple_edge_discovery_app --reload --port 8005

# Device Status API
run_device_status_api:
	source venv/bin/activate && \
	cd apis && \
    echo -e "\nLaunching FastAPI server for the Device Status API...\n" && \
    uvicorn main:device_status_app --reload --port 8006
