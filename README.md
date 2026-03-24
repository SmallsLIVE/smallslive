# Branch Mapping

- `develop_2026` -> [dev branch](https://github.com/SmallsLIVE/smallslive/tree/develop_2026)
- `production_2026` -> [prod branch](https://github.com/SmallsLIVE/smallslive/tree/production_2026)

# Development Guide using Docker Compose

This project uses Docker Compose for local development, staging, and production environments.

## Local Development

To start the local development environment:

```bash
docker compose -f docker-compose.dev.yaml up --build
```

### Common Commands (Local)

- **Run Migrations**:
  ```bash
  docker compose -f docker-compose.dev.yaml exec web python manage.py migrate
  ```
- **Create Superuser**:
  ```bash
  docker compose -f docker-compose.dev.yaml exec web python manage.py createsuperuser
  ```
- **Access Logs**:
  ```bash
  docker compose -f docker-compose.dev.yaml logs -f
  ```

## Staging Environment

To run the application in a staging environment:

```bash
docker compose -f docker-compose.stage.yaml up -d
```

## Production Environment

To run the application in production:

```bash
docker compose up -d
```

---

# Deployment Process

To deploy the application to EC2, follow these steps based on the environment:

1. **SSH into the EC2 instance**:
   ```bash
   ssh <user>@<ec2-ip-address>
   ```

2. **Navigate to the project directory**:
   ```bash
   cd smallslive
   ```

3. **Pull the latest changes**:
   ```bash
   git pull origin <branch-name>
   ```
   *(Use `develop_2026` for staging and `production_2026` for production)*

4. **Deploy using Docker Compose**:

   - **For Staging**:
     ```bash
     docker compose -f docker-compose.stage.yaml up -d --build
     ```

   - **For Production**:
     ```bash
     docker compose up -d --build
     ```
