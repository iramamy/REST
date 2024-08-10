# 🍲 Recipe App REST API - Test Driven Development 🛠️

## 📝 Overview

This project focuses on building a **REST API** for a recipe application using **Django** and **Django REST Framework (DRF)**. The primary goal is to implement **Test-Driven Development (TDD)** principles to ensure a robust and reliable application. The app is containerized with **Docker** to guarantee consistent development and deployment environments. There is no frontend; instead, user documentation and API testing are handled via **DRF Spectacular** and **Swagger**.

## 🌟 Features

- **🔗 REST API**: Build and manage a comprehensive API for the recipe application.
- **🧪 TDD Approach**: Developed with Test-Driven Development principles to ensure high code quality and reliability.
- **🐳 Dockerized**: Containerized using Docker for reproducibility and consistency across different environments.
- **📄 API Documentation**: Integrated **DRF Spectacular** for detailed and user-friendly API documentation.
- **🔍 API Testing**: Utilize **Swagger UI** for interactive API testing directly in your browser.

## 🚀 Getting Started

### 📋 Prerequisites

- **Docker**: Ensure Docker is installed on your machine.
- **Docker Compose**: Required for managing multi-container Docker applications.

### 🛠️ Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/iramamy/REST.git
   cd REST
   ```

2. **Build and Run the Docker Container**:

   ```bash
   docker compose build
   ```

3. **Run the Tests**:

   ```bash
   docker compose run --rm app -sh 'python manage.py test'
   ```

4. **Run the Server**:

   ```bash
   docker compose up
   ```

5. **Access the API Documentation**:

   Once the container is running, you can access the API documentation and interactive testing interface via:

   - **DRF Spectacular**: [http://localhost:8000/schema/](http://localhost:8000/schema/)
   - **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

## ⚠️ Notes:

- If you are running these commands on Linux, you may need to prepend **`sudo`** to the `docker compose` commands.
