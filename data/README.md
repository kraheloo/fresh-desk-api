# Data Layer - Migrations and Seeding Guide

This directory contains the database schema, migrations, seed data, and tools for managing the PostgreSQL database for the Fresh Desk API project.

## Directory Structure

```
data/
├── alembic/                 # Alembic migration framework
│   ├── versions/           # Migration scripts
│   ├── env.py             # Alembic environment configuration
│   └── script.py.mako     # Alembic template for generating migrations
├── files/                 # CSV seed data files
│   ├── departments.csv    # Department master data
│   ├── perimeters.csv     # Perimeter/Business Unit data
│   └── acl.csv            # Access Control List data
├── models.py              # SQLAlchemy ORM models
├── csv_loader.py          # CSV file parsing utilities
├── seed.py               # Data seeding script
├── database_connection.py # Database connection management
├── transaction_manager.py # Transaction and insertion logic
└── requirements.txt       # Python dependencies
```

## Database Models

### 1. Department Table (`departments`)

Represents organizational departments or business units.

**Columns:**
- `id` (Float, Primary Key) - Unique department identifier from source system (not auto-incremented)
- `name` (String[255], Not Null) - Department name

**Relationships:**
- Many-to-many with `Perimeter` through `perimeter_departments` join table

**Example:**
```
ID: 54000211509
Name: "Admin General - Administrative - G.014344.806.00"
```

### 2. Perimeter Table (`perimeters`)

Represents perimeters or business unit groupings.

**Columns:**
- `id` (Integer, Primary Key, Auto-increment) - Unique perimeter identifier
- `name` (String[255], Not Null) - Perimeter name

**Relationships:**
- Many-to-many with `Department` through `perimeter_departments` join table
- One-to-many with `ACL` (via `perimeter_id`)

**Example:**
```
ID: 1
Name: "Axians"
```

### 3. Perimeter-Department Association Table (`perimeter_departments`)

Join table for the many-to-many relationship between perimeters and departments.

**Columns:**
- `perimeter_id` (Integer, Foreign Key) - Reference to `perimeters.id`
- `department_id` (Float, Foreign Key) - Reference to `departments.id`
- Both columns form the composite primary key

### 4. ACL Table (`acls`)

Represents Access Control Lists - user permissions to perimeters or departments.

**Columns:**
- `id` (Integer, Primary Key, Auto-increment) - Unique ACL identifier
- `user_id` (String[255], Not Null) - User identifier/name
- `perimeter_id` (Integer, Foreign Key, Nullable) - Reference to `perimeters.id` (when access_level is 'P')
- `department_id` (Float, Foreign Key, Nullable) - Reference to `departments.id` (when access_level is 'D')
- `created_at` (DateTime with Timezone, Server Default) - Auto-populated on creation
- `updated_at` (DateTime with Timezone, Auto-update) - Auto-updated on modification

**Relationships:**
- Many-to-one with `Perimeter` (nullable)
- Many-to-one with `Department` (nullable)

**Notes:**
- Each ACL record has either a `perimeter_id` OR a `department_id` (not both)
- The access level (Perimeter vs Business Unit/Department) determines which foreign key is used

**Example:**
```
ID: 1 (auto-generated)
user_id: "User 1"
perimeter_id: 1
department_id: NULL
created_at: 2026-01-05 23:05:30.410006+00
updated_at: NULL
```

## CSV Data Models

### departments.csv

CSV file containing department master data loaded from the source system.

**Headers:** `ID, Name`

**Format:**
- `ID`: Numeric identifier (Float) matching the source system
- `Name`: Department name string

**Example:**
```
ID,Name
54000211509,"Admin General - Administrative - G.014344.806.00"
54000211523,"Admin General - Bank holidays - G.014344.827.00"
```

### perimeters.csv

CSV file containing perimeter/business unit data with their department associations.

**Headers:** `Id, PerimeterName, BU_Id, BU_Name`

**Format:**
- `Id`: Perimeter identifier (Integer)
- `PerimeterName`: Perimeter name string
- `BU_Id`: Associated department/business unit ID (Float)
- `BU_Name`: Associated department/business unit name

**Notes:**
- Multiple rows can share the same `Id` to represent multiple department associations for a single perimeter
- `BU_Id` and `BU_Name` must reference existing departments

**Example:**
```
Id,PerimeterName,BU_Id,BU_Name
1,Axians,54000211461,"DESKTOP 2026 AXIANS BASINGSTOKE"
1,Axians,54000211463,"DESKTOP 2026 AXIANS COVENTRY"
```

### acl.csv

CSV file containing user access control data.

**Headers:** `User, AccessLevel, Id`

**Format:**
- `User`: Username or user identifier (String)
- `AccessLevel`: Access level type - either `'P'` (Perimeter) or `'D'` (Department/Business Unit)
- `Id`: The identifier of the perimeter or department this user has access to

**Notes:**
- When `AccessLevel` is `'P'`, the `Id` refers to a perimeter ID
- When `AccessLevel` is `'D'`, the `Id` refers to a department ID

**Example:**
```
User,AccessLevel,Id
User 1,Perimeter,1
User 2,Perimeter,2
User 3,Business Unit,54000227472
User 4,Business Unit,54000377249
```

## Migrations

Alembic is used for database schema versioning and migrations. All migrations are stored in the `alembic/versions/` directory.

### Key Migrations

#### Initial Schema (`dcb14d4c921b_initial_schema.py`)
Creates the initial database schema with all core tables and relationships.

#### Modified ACL ID Column (`f89151b9118e_modified_acl_id_column.py`)
Converts the ACL table's `id` column from UUID type to INTEGER type with autoincrement capability.

**What it does:**
- Alters the `acls.id` column type from UUID() to Integer()
- Converts existing UUID values to integers using PostgreSQL's type casting
- Sets up auto-increment sequence for new inserts

### Running Migrations

**View migration status:**
```bash
alembic current
```

**Apply all pending migrations:**
```bash
alembic upgrade head
```

**Rollback to previous migration:**
```bash
alembic downgrade -1
```

**Create a new migration:**
```bash
# Auto-generate based on model changes
alembic revision --autogenerate -m "description_of_changes"

# Or create an empty migration to fill in manually
alembic revision -m "description_of_changes"
```

### Sequence Management

After type conversion migrations, PostgreSQL sequences may need manual configuration:

```sql
-- Create the sequence if it doesn't exist
CREATE SEQUENCE acls_id_seq;

-- Set the sequence as the default for the id column
ALTER TABLE acls ALTER COLUMN id SET DEFAULT nextval('acls_id_seq');

-- Initialize the sequence to start after existing IDs
SELECT setval('acls_id_seq', COALESCE((SELECT MAX(id) FROM acls), 0) + 1);
```

## Seeding the Database

The seeding process loads CSV data into the database in the correct order to maintain referential integrity.

### Prerequisites

1. PostgreSQL database is running and accessible
2. Database migrations have been applied (`alembic upgrade head`)
3. Python virtual environment is activated with dependencies installed

### Running the Seed Script

```bash
# From the data directory
python seed.py
```

### Seeding Process

The `seed.py` script performs the following steps:

1. **Load CSV Data** - Reads all CSV files from the `files/` directory
2. **Insert Departments** - Populates the `departments` table
3. **Insert Perimeters** - Populates the `perimeters` table and creates perimeter-department associations
4. **Insert ACLs** - Populates the `acls` table with user access permissions

### Logging

Seeding progress is logged with details about:
- Number of records successfully inserted
- Number of records skipped (duplicates)
- Any errors encountered during insertion

Example output:
```
2026-01-05 23:05:30,411 - INFO - ✓ Inserted 133 departments (0 skipped)
2026-01-05 23:05:30,412 - INFO - ✓ Inserted 10 perimeters (0 skipped)
2026-01-05 23:05:30,413 - INFO - ✓ Inserted 4 ACLs (0 skipped)
```

### Reseeding

If you need to reseed the database:

1. Clear existing data:
   ```bash
   # Using psql directly
   TRUNCATE TABLE acls CASCADE;
   TRUNCATE TABLE perimeter_departments CASCADE;
   TRUNCATE TABLE perimeters CASCADE;
   TRUNCATE TABLE departments CASCADE;
   ```

2. Reset auto-increment sequences:
   ```bash
   ALTER SEQUENCE perimeters_id_seq RESTART WITH 1;
   ALTER SEQUENCE acls_id_seq RESTART WITH 1;
   ```

3. Run the seed script:
   ```bash
   python seed.py
   ```

## Database Connection

The application uses environment variables for database configuration. Create a `.env` file or set these variables:

```
DATABASE_URL=postgresql://username:password@localhost:5432/freshdesk_db
```

Or configure in `database_connection.py` with your connection parameters.

## Dependencies

See `requirements.txt` for all Python dependencies. Key packages:
- `sqlalchemy` - ORM and database abstraction
- `alembic` - Database migration tool
- `psycopg2` - PostgreSQL adapter for Python

## Troubleshooting

### Migration Issues

**Error: "Sequence does not exist"**
- The migration may have changed column types without creating the sequence
- Create it manually using the SQL commands in the "Sequence Management" section

**Error: "Cannot cast UUID to INTEGER"**
- Use the USING clause in ALTER COLUMN statements: `USING (id::text::integer)`

### Seeding Issues

**Error: "Null value in column violates not-null constraint"**
- Check that all required CSV columns are present and correctly formatted
- Verify CSV headers match expected names (case-sensitive)

**Error: "Foreign key constraint violation"**
- Ensure dependencies are inserted in correct order: Departments → Perimeters → ACLs
- Verify all referenced IDs exist in parent tables

### Database Issues

**Connection refused**
- Verify PostgreSQL is running: `pg_isready -h localhost`
- Check connection parameters in `database_connection.py`
- Verify database and user exist

**Permission denied**
- Ensure PostgreSQL user has necessary permissions to create tables and sequences
- May need to run migrations as a superuser
