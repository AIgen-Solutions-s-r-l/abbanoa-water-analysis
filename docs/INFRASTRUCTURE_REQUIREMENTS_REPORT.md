# Infrastructure Requirements Report
## Abbanoa Water Analysis System

**Generated Date:** 2025-08-06  
**Project:** Abbanoa Water Infrastructure Monitoring & Analysis Platform  
**Version:** 2.0.0

---

## Executive Summary

The Abbanoa Water Analysis System is a comprehensive water infrastructure monitoring platform designed for the Sardinian water utility company. It processes time-series sensor data from water distribution nodes, provides real-time analytics, anomaly detection, and predictive maintenance capabilities. The system follows a hybrid architecture combining cloud services (Google Cloud Platform) with containerized microservices.

---

## 1. System Architecture Overview

### 1.1 Architecture Pattern
- **Type:** Hybrid Cloud Architecture
- **Pattern:** Microservices with Event-Driven Components
- **Deployment:** Container-based (Docker/Kubernetes)
- **Data Flow:** ETL Pipeline with Real-time and Batch Processing

### 1.2 Core Components

1. **Frontend Application (Next.js)**
   - Multi-tenant web dashboard
   - Real-time data visualization
   - Interactive infrastructure maps

2. **API Layer (FastAPI)**
   - RESTful API endpoints
   - Authentication & authorization
   - Data aggregation services

3. **Data Processing Layer**
   - ETL pipelines
   - ML model execution
   - Anomaly detection services

4. **Data Storage**
   - Cold Storage: Google BigQuery
   - Warm Storage: PostgreSQL + TimescaleDB
   - Cache Layer: Redis

5. **Monitoring & Observability**
   - Prometheus metrics collection
   - Grafana dashboards
   - Application logging

---

## 2. Infrastructure Components

### 2.1 Runtime Requirements

#### Node.js Environment
- **Version:** ≥18.0.0
- **NPM Version:** ≥8.0.0
- **Purpose:** Frontend application runtime

#### Python Environment
- **Version:** 3.9+ (implied from dependencies)
- **Purpose:** Backend API, data processing, ML services

### 2.2 Containerization

#### Docker Requirements
- **Docker Engine:** 20.10+
- **Docker Compose:** 3.8+
- **Container Images:**
  - `node:18-alpine` (Frontend)
  - `python:3.9-slim` (Backend services)
  - `timescale/timescaledb:latest-pg14` (Database)
  - `redis:7-alpine` (Cache)
  - `nginx:alpine` (Reverse proxy)
  - `prom/prometheus:latest` (Metrics)
  - `grafana/grafana:latest` (Dashboards)

### 2.3 Orchestration

#### Kubernetes (Production)
- **Version:** 1.21+
- **Components:**
  - Namespaces for isolation
  - StatefulSets for databases
  - Deployments for stateless services
  - ConfigMaps and Secrets management
  - PersistentVolumeClaims for data persistence

#### Google Kubernetes Engine (GKE)
- **Cluster Type:** Regional cluster
- **Node Pool:** Autoscaling (1-10 nodes)
- **Machine Type:** n2-standard-2 minimum
- **Region:** europe-west1

---

## 3. Data Storage Infrastructure

### 3.1 Primary Data Stores

#### Google BigQuery (Cold Storage)
- **Project ID:** abbanoa-464816
- **Dataset:** water_infrastructure
- **Location:** EU
- **Purpose:** Historical data, analytics, ML training
- **Tables:**
  - Sensor readings
  - Node metadata
  - Anomaly records
  - ML predictions

#### PostgreSQL + TimescaleDB (Warm Storage)
- **Version:** PostgreSQL 14 + TimescaleDB
- **Purpose:** Operational data, real-time queries
- **Extensions:**
  - TimescaleDB (time-series optimization)
  - PostGIS (geospatial data)
- **Configuration:**
  - 1GB shared buffers
  - 200 max connections
  - Hypertables with 1-week chunks

#### Redis Cache
- **Version:** 7-alpine
- **Purpose:** Session management, query caching
- **Configuration:**
  - 4GB max memory (production)
  - LRU eviction policy
  - AOF persistence

### 3.2 Storage Requirements

- **PostgreSQL Volume:** 100GB+ SSD
- **Redis Volume:** 10GB SSD
- **Backup Storage:** 500GB (Google Cloud Storage)
- **Log Storage:** 50GB

---

## 4. Network Infrastructure

### 4.1 External Services

#### Google Cloud Platform Services
- **BigQuery:** Data warehouse
- **Cloud Storage:** Backup and file storage
- **Cloud Build:** CI/CD pipeline
- **Cloud Run:** Serverless deployment option
- **Container Registry:** Docker image storage
- **Cloud IAM:** Authentication and authorization

#### Third-Party Services
- **SMTP Server:** Email notifications
  - Host: smtp.gmail.com
  - Port: 587
  - TLS enabled

### 4.2 Network Configuration

#### Ingress/Load Balancing
- **NGINX:** Reverse proxy and load balancer
- **Ports:**
  - 80/443: Web traffic
  - 8000: API service
  - 3000: Frontend (development)
  - 8501: Streamlit dashboard (legacy)
  - 6379: Redis
  - 5432: PostgreSQL
  - 9090: Prometheus
  - 3000: Grafana

#### Internal Networking
- **Docker Network:** Bridge network (abbanoa-network)
- **Service Discovery:** DNS-based (Kubernetes)
- **Security:** Network policies for pod-to-pod communication

---

## 5. Security Requirements

### 5.1 Authentication & Authorization
- **GCP Service Account:** For BigQuery access
- **JWT Tokens:** API authentication
- **PostgreSQL Users:** Database access control
- **Redis Auth:** Password protection

### 5.2 Secrets Management
- **Google Cloud Secret Manager:** Production secrets
- **Kubernetes Secrets:** Application credentials
- **Environment Variables:** Configuration injection

### 5.3 SSL/TLS
- **HTTPS:** Required for production
- **SSL Certificates:** Let's Encrypt or managed certificates
- **TLS Version:** 1.2 minimum

---

## 6. Development Dependencies

### 6.1 Frontend (Next.js)

#### Production Dependencies
- **Core:**
  - next: 15.3.5
  - react: 19.0.0
  - react-dom: 19.0.0

- **UI/Visualization:**
  - leaflet: 1.9.4 (Maps)
  - react-leaflet: 5.0.0
  - recharts: 3.1.0 (Charts)
  - lucide-react: 0.525.0 (Icons)

#### Development Dependencies
- **Build Tools:**
  - typescript: 5.x
  - tailwindcss: 4.x
  - @tailwindcss/postcss: 4.x

- **Testing:**
  - jest: 30.0.4
  - @testing-library/react: 16.3.0
  - @testing-library/jest-dom: 6.6.3

- **Linting:**
  - eslint: 9.x
  - eslint-config-next: 15.3.5

### 6.2 Backend (Python)

#### Core Dependencies
- **Web Framework:**
  - fastapi: 0.104.1
  - uvicorn: 0.25.0
  - streamlit: 1.29.0 (Legacy dashboard)

- **Data Processing:**
  - pandas: 2.1.4
  - numpy: 1.25.2
  - scikit-learn: 1.3.2

- **Database:**
  - asyncpg: 0.29.0 (PostgreSQL)
  - google-cloud-bigquery: 3.13.0
  - redis: 5.0.1

- **Utilities:**
  - httpx: 0.25.2 (HTTP client)
  - joblib: 1.3.2 (Parallel processing)
  - apscheduler: 3.10.4 (Job scheduling)
  - plotly: 5.17.0 (Visualization)

### 6.3 Mock Backend (Node.js)
- express: 4.18.2
- cors: 2.8.5
- jsonwebtoken: 9.0.2
- bcryptjs: 2.4.3

---

## 7. CI/CD Infrastructure

### 7.1 Build Pipeline
- **Google Cloud Build:** Automated builds
- **Docker Multi-stage Builds:** Optimized images
- **Build Timeout:** 20 minutes

### 7.2 Deployment Pipeline
- **Target Environments:**
  - Development: Local Docker Compose
  - Staging: GKE Staging Cluster
  - Production: GKE Production Cluster / Cloud Run

### 7.3 Version Control
- **Git Repository:** Source code management
- **Branch Strategy:** Main branch with feature branches
- **Release Tags:** Semantic versioning

---

## 8. Monitoring & Observability

### 8.1 Metrics Collection
- **Prometheus:** Time-series metrics
  - Application metrics
  - System metrics
  - Custom business metrics

### 8.2 Visualization
- **Grafana Dashboards:**
  - System performance
  - Application health
  - Business KPIs
  - Water infrastructure metrics

### 8.3 Logging
- **Log Aggregation:** Centralized logging
- **Log Levels:** INFO, WARNING, ERROR, CRITICAL
- **Log Format:** JSON structured logging
- **Retention:** 30 days

---

## 9. Backup & Disaster Recovery

### 9.1 Backup Strategy
- **Database Backups:**
  - PostgreSQL: Daily automated backups
  - Retention: 30 days
  - Storage: Google Cloud Storage

- **BigQuery Backups:**
  - Table snapshots
  - Export to Cloud Storage

### 9.2 Recovery Objectives
- **RPO (Recovery Point Objective):** 24 hours
- **RTO (Recovery Time Objective):** 4 hours

---

## 10. Scaling Requirements

### 10.1 Horizontal Scaling
- **API Services:** 1-10 replicas (auto-scaling)
- **Frontend:** 1-5 replicas
- **Workers:** 1-5 processing workers

### 10.2 Vertical Scaling
- **Database:**
  - CPU: 2-8 cores
  - Memory: 4-16 GB
  - Storage: Auto-expanding

### 10.3 Performance Targets
- **API Response Time:** <500ms p95
- **Dashboard Load Time:** <3 seconds
- **Data Processing Latency:** <5 minutes
- **Concurrent Users:** 100+

---

## 11. Environment Configuration

### 11.1 Required Environment Variables

#### BigQuery Configuration
```
BIGQUERY_PROJECT_ID=abbanoa-464816
BIGQUERY_DATASET_ID=water_infrastructure
BIGQUERY_LOCATION=EU
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

#### Database Configuration
```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=abbanoa
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<secure_password>
```

#### Redis Configuration
```
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<optional_password>
```

#### API Configuration
```
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

#### Frontend Configuration
```
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=http://api:8000
```

### 11.2 Optional Configuration

#### Monitoring
```
PROMETHEUS_PORT=9090
GRAFANA_PASSWORD=admin
```

#### Notifications
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=<email>
SMTP_PASSWORD=<app_password>
ALERT_RECIPIENTS=alerts@domain.com
```

#### ML/Analytics
```
ANOMALY_Z_SCORE=3.0
ANOMALY_MIN_POINTS=10
ANOMALY_WINDOW_HOURS=24
```

---

## 12. Development Setup

### 12.1 Local Development Requirements
- Docker Desktop 4.0+
- Python 3.9+
- Node.js 18+
- Git
- Google Cloud SDK (for BigQuery access)

### 12.2 Quick Start Commands

#### Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python -m src.infrastructure.database.postgres_manager

# Start API server
uvicorn src.presentation.api.app:app --reload
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Docker Compose (Full Stack)
```bash
# Development environment
docker-compose -f docker-compose.dev.yml up

# Production environment
docker-compose -f docker-compose.prod.yml up
```

---

## 13. Production Deployment

### 13.1 Prerequisites
1. Google Cloud Project with billing enabled
2. Service account with appropriate permissions
3. Docker images built and pushed to registry
4. SSL certificates configured
5. Domain name configured

### 13.2 Deployment Steps

1. **Database Setup**
   - Deploy PostgreSQL + TimescaleDB
   - Run schema migrations
   - Configure backups

2. **Cache Layer**
   - Deploy Redis instance
   - Configure persistence

3. **Backend Services**
   - Deploy API service
   - Deploy ETL workers
   - Configure auto-scaling

4. **Frontend**
   - Build production bundle
   - Deploy to web server/CDN
   - Configure routing

5. **Monitoring**
   - Deploy Prometheus
   - Configure Grafana
   - Set up alerts

6. **Load Balancer**
   - Configure NGINX
   - Set up SSL termination
   - Configure health checks

---

## 14. Cost Estimation

### 14.1 Google Cloud Platform (Monthly)
- **BigQuery:** ~$50-200 (based on query volume)
- **GKE Cluster:** ~$150-300
- **Cloud Storage:** ~$20-50
- **Network Egress:** ~$50-100
- **Total GCP:** ~$270-650/month

### 14.2 Infrastructure Sizing
- **Minimum (Dev/Test):** 2 nodes, 4 vCPU, 8GB RAM
- **Recommended (Production):** 4 nodes, 8 vCPU, 32GB RAM
- **High Availability:** 6+ nodes, 16+ vCPU, 64GB+ RAM

---

## 15. Compliance & Regulations

### 15.1 Data Privacy
- GDPR compliance for EU data
- Data residency in EU regions
- User consent management

### 15.2 Security Standards
- TLS 1.2+ for data in transit
- Encryption at rest for sensitive data
- Regular security updates

### 15.3 Audit & Logging
- Comprehensive audit trails
- User activity logging
- Data access monitoring

---

## 16. Known Limitations & Considerations

### 16.1 Technical Limitations
- BigQuery queries have cost implications
- Real-time processing limited by ETL frequency
- Cache invalidation requires careful management

### 16.2 Scalability Considerations
- Database connections pool limit
- BigQuery concurrent query limits
- Network bandwidth for large data transfers

### 16.3 Maintenance Windows
- Database maintenance: Monthly
- Security patches: As required
- Feature updates: Bi-weekly sprints

---

## 17. Support & Documentation

### 17.1 Internal Documentation
- `/docs`: Technical documentation
- `/docs/architecture`: System architecture
- `/docs/api`: API documentation
- `/docs/guides`: User and developer guides

### 17.2 External Resources
- Google Cloud Documentation
- PostgreSQL/TimescaleDB Documentation
- Docker/Kubernetes Documentation
- Next.js/React Documentation

### 17.3 Support Channels
- GitHub Issues: Bug reports and feature requests
- Internal Wiki: Operational procedures
- Slack/Teams: Team communication

---

## 18. Recommendations

### 18.1 High Priority
1. **Implement comprehensive monitoring** before production deployment
2. **Set up automated backups** with tested restore procedures
3. **Configure auto-scaling** for handling peak loads
4. **Implement rate limiting** on API endpoints
5. **Set up alerting** for critical system events

### 18.2 Medium Priority
1. **Optimize BigQuery queries** to reduce costs
2. **Implement caching strategies** for frequently accessed data
3. **Set up CI/CD pipelines** for automated deployments
4. **Create runbooks** for common operational tasks
5. **Implement feature flags** for gradual rollouts

### 18.3 Future Enhancements
1. **Multi-region deployment** for high availability
2. **GraphQL API** for flexible data queries
3. **Real-time streaming** with Apache Kafka/Pub/Sub
4. **Advanced ML pipelines** with Vertex AI
5. **Mobile application** for field operators

---

## Conclusion

The Abbanoa Water Analysis System is a sophisticated platform requiring a robust infrastructure setup. The hybrid architecture leveraging Google Cloud Platform services with containerized microservices provides the flexibility and scalability needed for water infrastructure monitoring at scale.

Key success factors include:
- Proper resource allocation for databases
- Effective caching strategies
- Comprehensive monitoring and alerting
- Regular maintenance and updates
- Clear documentation and operational procedures

With the infrastructure requirements outlined in this report properly implemented, the system will be capable of handling the data processing, analytics, and visualization needs of the Sardinian water utility network effectively.

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-08-06  
**Next Review:** 2025-09-06