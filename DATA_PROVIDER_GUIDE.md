# Data Provider Configuration Guide

## Overview
The application now supports two data providers:
- **CsvDataService**: Reads data from CSV files (default)
- **DBDataService**: Reads data from PostgreSQL database

## Switching Between Providers

To change the data provider, modify the `appsettings.json` file in the `backend.api` folder:

### Using CSV Files (Default)
```json
"Database": {
  "ConnectionString": "postgresql://postgres:Protocol_101!@localhost/freshdesk",
  "UseDatabase": false
}
```

### Using PostgreSQL Database
```json
"Database": {
  "ConnectionString": "postgresql://postgres:Protocol_101!@localhost/freshdesk",
  "UseDatabase": true
}
```

## Implementation Details

### Files Created/Modified:
1. **Services/DBDataService.cs** (NEW)
   - Implements the `ICsvDataService` interface
   - Queries PostgreSQL database for departments, perimeters, and user ACLs
   - Uses Npgsql for database connectivity

2. **Program.cs** (MODIFIED)
   - Added conditional service registration based on `Database:UseDatabase` configuration
   - If `UseDatabase` is true, registers `DBDataService`, otherwise `CsvDataService`

3. **appsettings.json** (MODIFIED)
   - Added `Database` section with connection string and switch flag

4. **backend.api.csproj** (MODIFIED)
   - Added Npgsql v8.0.6 NuGet package for PostgreSQL connectivity

## Database Schema Expected

The `DBDataService` expects the following tables in PostgreSQL:

### departments table
- `id` (bigint, primary key)
- `name` (text)

### perimeters table
- `id` (int, primary key)
- `perimeter_name` (text)
- `bu_id` (bigint)
- `bu_name` (text)

### user_acl table
- `id` (int, primary key)
- `user` (text)
- `access_level` (text)

## Usage Notes

- Both services implement the same `ICsvDataService` interface, ensuring the rest of the application works identically regardless of which provider is used
- Data is cached in memory by both services to improve performance
- Error handling is built-in with appropriate logging
- The configuration change requires an application restart to take effect
