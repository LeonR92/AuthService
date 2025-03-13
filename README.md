[![CI](https://github.com/LeonR92/BookStore/actions/workflows/ci.yml/badge.svg)](https://github.com/LeonR92/BookStore/actions/workflows/ci.yml)
![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)


# Scalable Authentication Service

A production-ready authentication service demonstrating enterprise-level architecture and security practices.

## Architecture Overview

This authentication service implements a robust, scalable architecture using:

- **Database Layer**
  - PostgreSQL with 1 write replica and 3 read replicas
  - HAProxy for intelligent read query distribution
  - PGBouncer for connection pooling
  - Repository pattern for clean data access abstraction

- **Caching & Performance**
  - Redis for session management and token storage
  - Nginx for request handling and static asset serving
  - Optimized Docker Compose configuration

- **Frontend**
  - TailwindCSS for responsive dashboard UI
  - Minimal design focused on authentication flows

## Security Features

- **Multi-Factor Authentication (MFA)**
  - Optional MFA during registration
  - PyOTP integration for time-based one-time passwords
  - User-controlled MFA activation/deactivation

- **Rate Limiting**
  - Request throttling to prevent brute force attacks
  - IP-based and account-based rate limiting strategies

- **Honeypot Protection**
  - Invisible form fields to catch automated submissions
  - Automated flagging of suspicious authentication attempts

## Development Practices

- **Continuous Integration**
  - GitHub Actions workflow for automated testing
  - pytest suite covering critical authentication paths
  - Code quality and security scanning

- **Containerization**
  - Multi-service Docker Compose setup
  - Optimized initialization sequence
  - Network isolation between service layers

## Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/auth-service.git
cd auth-service

# Start the services
docker-compose up
```

Visit `http://localhost:80` to access the authentication dashboard.

## Testing

```bash
# Run the test suite
pytest

# Run with coverage
pytest --cov=app tests/
```

## License

[MIT](LICENSE)