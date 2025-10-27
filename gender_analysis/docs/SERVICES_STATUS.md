# System Services Status

**Date**: 2024-10-26  
**System**: Gender & Age Analysis

---

## ✅ Installed Services

| Service | Version | Status | Port | GUI |
|---------|---------|--------|------|-----|
| **PostgreSQL** | 15.14 | ✅ Running | 5432 | ✅ pgAdmin 4 |
| **Redis** | 8.2.2 | ✅ Running | 6379 | ✅ Redis Insight |
| **Prometheus** | 3.7.2 | ✅ Running | 9090 | Web UI |

---

## 🔍 Service Verification

### PostgreSQL
```bash
# Check service
brew services list | grep postgresql
# Result: postgresql@15  started

# Connect
psql -U autoeyes -d gender_analysis -c "\dt"
```

### Redis
```bash
# Check service
brew services list | grep redis
# Result: redis  started

# Connect
redis-cli ping
# Result: PONG

# View data
redis-cli KEYS "*"
```

### Prometheus
```bash
# Check service
brew services list | grep prometheus
# Result: prometheus  started

# Access UI
open http://localhost:9090
```

---

## 🖥️ GUI Applications

### pgAdmin 4
- **Location**: `/Applications/pgAdmin 4.app`
- **Purpose**: Database management
- **Connection**:
  - Host: localhost
  - Port: 5432
  - Database: gender_analysis

### Redis Insight
- **Location**: `/Applications/Redis Insight.app`
- **Purpose**: Redis monitoring
- **Connection**:
  - Host: localhost
  - Port: 6379

### Prometheus Web UI
- **URL**: http://localhost:9090
- **Purpose**: Metrics & monitoring
- **Query**: PromQL queries

---

## 📊 Quick Checks

```bash
# PostgreSQL
psql -U autoeyes -d gender_analysis -c "SELECT COUNT(*) FROM person_analysis;"

# Redis
redis-cli LLEN gender_analysis

# Prometheus
curl http://localhost:9090/api/v1/targets
```

---

**All services are running and ready!** ✅

