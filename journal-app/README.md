# Gratitude Journal

## Overview
The Gratitude Journal application is a microservice-based project built using Flask. It is designed for playing around with OpenTelemetry and observability tools and testing simulated delays and errors. The application consists of four main services:

- **Auth Service**:  
  Handles user registration and login (with simulated delays) using Flask, Flask-SQLAlchemy, and Werkzeug for secure password storage.

- **Journal Service**:  
  Provides REST API endpoints for creating, reading, updating, and deleting journal entries. It uses Flask-SQLAlchemy and a shared SQLite database.

- **Quote Service**:  
  Fetches a daily quote from an external API (`https://api.quotable.io/random`) and caches it in the database. It also randomly simulates errors by occasionally omitting the SSL verification.

- **UI Service**:  
  Serves as the frontend for the application. It uses Flask with Flask-Login for user session management and renders HTML templates using the Bulma CSS framework. The UI service interacts with the other services by making HTTP calls to their API endpoints.

## How the Services Interact
- All services are containerized and defined in the `docker-compose.yml` file.
- **Inter-Service Communication**:  
  The UI service interacts with the Auth, Journal, and Quote services via HTTP using the internal Docker network (using service names like `auth`, `journal`, and `quote`).
- **Shared Database**:  
  All services share a common SQLite database mounted via a Docker volume (`data-volume`). This allows for centralized storage of user data, journal entries, and daily quotes.


## Building and Running the Application

You can build and run the application using either the provided Makefile (which wraps Docker Compose commands) or by running Docker Compose commands directly.

**Using Make:**
- **build**: Build all Docker containers.
  ```bash
  make build
  ```
- **run**: Start the application (all services) in the foreground.
  ```bash
  make run
  ```
- **reload**: Stop running containers, rebuild, and start up again.
  ```bash
  make reload
  ```
- **logs**: Tail the logs from all containers.
  ```bash
  make logs
  ```
- **down**: Stop and remove all running containers.
  ```bash
  make down
  ```

**Using Docker Compose Directly:**
- Build and run the containers:
  ```bash
  docker-compose up --build
  ```
- Stop the application:
  ```bash
  docker-compose down
  ```

## Accessing the Application
Once all the containers are running, open your web browser and navigate to [http://localhost:5000](http://localhost:5000) to access the UI service.

## Observability and Testing
This application includes intentional delays and error simulations (e.g., a random delay in the login service, random SSL verification errors in the quote service). These features are designed to help test and experiment with observability tools like logging, tracing, or performance monitoring.


---