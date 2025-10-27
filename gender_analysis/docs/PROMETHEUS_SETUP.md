# Prometheus Setup Guide

**Date**: 2024-10-26  
**Status**: ✅ Installed & Running

---

## ✅ Installation Complete

- ✅ Prometheus 3.7.2 installed
- ✅ Service running on port 9090
- ✅ Configuration ready

---

## 🚀 Access Prometheus

### Web UI
- URL: http://localhost:9090
- PromQL queries available
- Metrics dashboard

### API
- Endpoint: http://localhost:9090/api/v1
- Query: http://localhost:9090/api/v1/query
- Metrics: http://localhost:9090/api/v1/query?query=up

---

## 📊 Metrics Available

### Gender Analysis Metrics

```
# Faces detected
faces_detected_total

# Gender classifications by gender
gender_classified_total{gender="male"}
gender_classified_total{gender="female"}

# Age estimations
age_estimated_total

# Processing time
analysis_processing_time_seconds
feature_extraction_time_seconds

# System status
active_cameras
task_queue_size
feature_cache_size
```

---

## 🔍 Example Queries

### Get total faces detected
```promql
faces_detected_total
```

### Get gender distribution
```promql
gender_classified_total
```

### Get average processing time
```promql
rate(analysis_processing_time_seconds[5m])
```

### Get queue size
```promql
task_queue_size
```

---

## 🛠️ Service Management

### Start Prometheus
```bash
brew services start prometheus
```

### Stop Prometheus
```bash
brew services stop prometheus
```

### Restart Prometheus
```bash
brew services restart prometheus
```

### Check Status
```bash
brew services list | grep prometheus
```

---

## ✅ Verification

```bash
# Check Prometheus is running
curl http://localhost:9090/api/v1/status/config

# View metrics
curl http://localhost:9090/api/v1/label/__name__/values
```

---

**Prometheus is ready for monitoring!** 📊

