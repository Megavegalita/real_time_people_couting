# pgAdmin 4 Setup Guide

**Date**: 2024-10-26  
**Purpose**: Connect to gender_analysis database

---

## 🚀 Quick Start

### 1. Open pgAdmin 4
- pgAdmin is now installed at: `/Applications/pgAdmin 4.app`
- Open it from Launchpad or Applications folder

### 2. First Time Setup

When you first open pgAdmin, you'll need to:
1. Set a master password (to protect pgAdmin configuration)
2. This password is NOT your PostgreSQL password
3. Remember this password for future launches

---

## 🔌 Connect to Database

### Connection Information

```
Host: localhost
Port: 5432
Maintenance database: postgres
Username: autoeyes
Password: (leave empty - no password set)
```

### Steps to Connect

1. **Right-click** on "Servers" in the left panel
2. **Select**: "Register" → "Server"
3. **General Tab**:
   - Name: `Local PostgreSQL` (or any name you like)
   
4. **Connection Tab**:
   - Host name/address: `localhost`
   - Port: `5432`
   - Maintenance database: `postgres`
   - Username: `autoeyes`
   - Password: (leave empty or enter your password if you set one)
   - ✅ Save password (optional)

5. **Click**: "Save"

---

## 📊 View gender_analysis Database

Once connected:

1. **Expand**: Servers → Local PostgreSQL → Databases
2. **You'll see**: `gender_analysis` database
3. **Click**: gender_analysis
4. **Expand**: Schemas → public → Tables

### Tables Created

You'll find these tables:
- ✅ `person_analysis` - Main results table
- ✅ `cameras` - Camera configurations
- ✅ `daily_stats` - Daily statistics

---

## 🧪 Test Connection

### From Terminal

```bash
# Test connection
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
psql -U autoeyes -d gender_analysis -c "\dt"
```

Should show:
```
public | cameras         | table | autoeyes
public | daily_stats     | table | autoeyes  
public | person_analysis | table | autoeyes
```

---

## 📋 Table Schemas

### person_analysis Table

```sql
CREATE TABLE person_analysis (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(50) NOT NULL,
    person_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    gender VARCHAR(10) NOT NULL,  -- 'male' or 'female'
    gender_confidence FLOAT NOT NULL,
    age INTEGER NOT NULL,
    age_confidence FLOAT NOT NULL,
    location VARCHAR(100),
    direction VARCHAR(20),  -- 'IN' or 'OUT'
    face_features JSONB,  -- 128-dim vector
    created_at TIMESTAMP DEFAULT NOW()
);
```

### cameras Table

```sql
CREATE TABLE cameras (
    camera_id VARCHAR(50) PRIMARY KEY,
    camera_name VARCHAR(100) NOT NULL,
    stream_url TEXT NOT NULL,
    location VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### daily_stats Table

```sql
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    total_people INTEGER DEFAULT 0,
    male_count INTEGER DEFAULT 0,
    female_count INTEGER DEFAULT 0,
    avg_age FLOAT,
    hour_breakdown JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔍 Useful pgAdmin Queries

### View All Tables

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### View person_analysis Structure

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'person_analysis';
```

### Check Table Counts

```sql
SELECT 
    (SELECT COUNT(*) FROM person_analysis) as analysis_count,
    (SELECT COUNT(*) FROM cameras) as camera_count,
    (SELECT COUNT(*) FROM daily_stats) as stats_count;
```

---

## ✅ Connection Test

### Quick Test Query

In pgAdmin Query Tool:

```sql
-- Test connection
SELECT version();

-- Should return: PostgreSQL 15.14 (Homebrew)...

-- Show tables
SELECT * FROM information_schema.tables 
WHERE table_schema = 'public';

-- Should show 3 tables
```

---

## 🎯 Next Steps

1. ✅ Open pgAdmin 4
2. ✅ Connect to localhost server
3. ✅ Browse `gender_analysis` database
4. ✅ Verify tables exist
5. Ready for Phase 2!

---

**Status**: ✅ pgAdmin 4 Installed  
**Location**: /Applications/pgAdmin 4.app  
**Database**: gender_analysis  
**Tables**: 3 tables ready for Phase 2

