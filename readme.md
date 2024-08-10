# Recipe App REST API - Test Driven Development

## Overview

This project involves building a REST API for a recipe application using Django and Django REST Framework (DRF). The primary goal is to apply Test-Driven Development (TDD) principles throughout the development process. The application is containerized using Docker to ensure reproducibility. There is no frontend; instead, user documentation and API testing are handled through DRF Spectacular and Swagger.

## Features

- **REST API**: Build and manage a recipe application API.
- **TDD Approach**: Developed with a Test-Driven Development methodology to ensure reliability and robustness.
- **Dockerized**: Containerized using Docker for consistent development and deployment environments.
- **API Documentation**: Integrated DRF Spectacular for user-friendly API documentation.
- **API Testing**: Use Swagger UI for interactive API testing directly in the browser.

## Getting Started

### Prerequisites

- **Docker**
- **Docker Compose**

## Installation

- Clone the repository:

```bash
git clone https://github.com/iramamy/REST.git
cd REST
```

- Build and run the Docker container:

```bash
docker compose build
```

- Run the tests

```bash
docker compose run --rm app -sh 'python manage.py test'
```

- Run the server:

```bash
docker compose up
```

- Access the API Documentation:

Once the container is running, you can access the API documentation and interactive testing interface via:

**DRF Spectacular**: [http://localhost:8000/schema/](http://localhost:8000/schema/)
**Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

## Notes:

- If you are running these commands on Linux, you may need to prepend `**sudo**` to the `docker compose` commands.
