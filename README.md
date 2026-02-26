# AdvancedRAGEngine
Advanced End-to-End RAG system

This repository contains an advanced multi-tenant end-to-end Retrieval-Augmented Generation (RAG) system. The system is designed to be flexible, scalable, and easy to deploy, making it suitable for a wide range of applications.
## Features
- **Multi-Tenancy**: Supports multiple tenants with isolated data and configurations.
- **Scalable Architecture**: Built using microservices architecture to ensure scalability and maintainability.
- **Authentication and Authorization**: Implements robust authentication and authorization mechanisms to secure tenant data.

## Technologies Used
- **Backend**: Python, FastAPI
- **Database**: SQLAlchemy, SQLite(for development)
- **Authentication**: OAuth2, JWT
- **Frontend**: React.js, HTML, CSS, JavaScript
- **Monitoring**: Prometheus, Grafana

## System Architecture
The system is structured into several components:
1. **Backend API**: A FastAPI-based backend that handles all business logic, data management, and authentication.
2. **Frontend Application**: A React.js-based frontend that provides a user-friendly interface for tenants and administrators to interact with the system.
3. **Database**: A relational database (SQLite for development) to store tenant data, user information, and configurations.
4. **Authentication Service**: A service that manages user authentication and authorization using OAuth2 and JWT.
5. **Monitoring and Analytics**: Integration with Prometheus and Grafana for monitoring system performance and usage analytics.


## Key Components
- **Tenant Management**: Allows administrators to create and manage tenants, each with its own isolated data and configurations.
- **User Management**: Enables administrators and editors to manage users within their respective tenants, including role-based access control.

## AI Assistance or Development Tools
- **Code Generation**: Utilizes Github Copilot to assist in code generation for backend and frontend development, reducing development time and improving code quality.
- **Documentation Generation**: Github Copilot is used to generate comprehensive documentation for the API and system architecture, making it easier for developers to understand and contribute to the project.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ShivaniShah0218/AdvancedRAGEngine.git
   ```
2. Navigate to the project directory:
   ```bash
   cd AdvancedRAGEngine
   ```
3. Ensure you have Python 3.8+ installed and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Required dependencies can be installed using pip:
   ```bash
   pip install -r requirements.txt
   ```
5. Install the frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
6. Build the frontend:
   ```bash
   npm run build
   ```
7. Run the frontend development server:
   ```bash
   npm start
   ```
8. Install prometheus and grafana for monitoring:
   - [Prometheus Installation Guide](https://prometheus.io/docs/prometheus/latest/installation/)
   - [Grafana Installation Guide](https://grafana.com/docs/grafana/latest/installation/)
9. Configure Prometheus to scrape metrics from the backend server and set up Grafana dashboards for monitoring.
10. Configure the backend server by setting environment variables for database connection, authentication secrets, and other configurations as needed.
11. Run the backend script:
   ```bash
   python -m backend.run_server.py
   ```
## Usage
- Access the frontend application at `http://localhost:3001` and log in with admin credentials.
- Use the admin dashboard to manage tenants, view analytics.
- Tenants can log in to their respective dashboards to manage their users and configurations.
- Admin can add organizations, manage editors and users, see all organizations from the admin dashboard. 
- Editors can add users to their organization and manage their configurations.
- Users can log in to their dashboards to view and manage their data.
- Monitor the system using Prometheus and Grafana to ensure optimal performance and identify any issues.
- For detailed API documentation, refer to the backend codebase and the FastAPI auto-generated documentation available at `http://localhost:8000/docs` when the backend server is running.
- For any issues or contributions, please open an issue or submit a pull request on the GitHub repository.


## License
This project is licensed under the Apache-2.0 License.
