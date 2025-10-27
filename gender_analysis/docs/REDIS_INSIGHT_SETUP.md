# Redis Insight GUI Setup

**Date**: 2024-10-26  
**Status**: ✅ Installed & Ready

---

## ✅ Installation Complete

- ✅ Redis Insight GUI installed
- ✅ Location: `/Applications/Redis Insight.app`
- ✅ Redis server running on localhost:6379

---

## 🚀 Quick Start

### 1. Open Redis Insight
- Location: `/Applications/Redis Insight.app`
- Or search "Redis Insight" in Launchpad

### 2. Add Connection
- Click "Add Redis Database"
- Connection details:
  - **Name**: Local Redis
  - **Host**: localhost
  - **Port**: 6379
  - **Username**: (leave empty)
  - **Password**: (leave empty)
- Click "Add Database"

### 3. View Data
- Browse keys in the database
- Monitor real-time data
- View queue contents

---

## 🔍 Monitoring Queue

### View Task Queue
```bash
# In Redis Insight, browse keys:
# - gender_analysis:queue
# - gender_analysis:results
```

### Check Queue Size
```bash
redis-cli
> LLEN gender_analysis
(integer) 5
```

---

## ✅ System Services Running

| Service | Status | Port |
|---------|--------|------|
| PostgreSQL | ✅ Running | 5432 |
| Redis | ✅ Running | 6379 |
| Prometheus | ✅ Running | 9090 |

---

**Redis Insight is ready for use!**

