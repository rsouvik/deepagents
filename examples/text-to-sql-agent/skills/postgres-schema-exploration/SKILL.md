---
name: postgres-schema-exploration
description: Explores PostgreSQL schemas, tables, columns, and relationships using MCP database tools. Use when the user asks what tables exist, requests schema discovery, asks how entities are related, or needs PostgreSQL-safe metadata queries.
---

# PostgreSQL Schema Exploration Skill

## Workflow

### 1. Identify schema scope first
Start with PostgreSQL metadata discovery before writing business queries.

Use a query equivalent to:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

### 2. Inspect columns for target tables
For each relevant table, inspect column names, types, nullability, and defaults.

Use a query equivalent to:

```sql
SELECT
  table_schema,
  table_name,
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = '<table_name>'
ORDER BY ordinal_position;
```

### 3. Map primary and foreign keys
Capture join paths before building analytical queries.

Use a query equivalent to:

```sql
SELECT
  tc.table_schema,
  tc.table_name,
  kcu.column_name,
  tc.constraint_type,
  ccu.table_schema AS foreign_table_schema,
  ccu.table_name AS foreign_table_name,
  ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
 AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
 AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY')
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_type, kcu.ordinal_position;
```

### 4. Answer with a schema map
Return:
- available schemas and tables
- key columns and data types
- PK/FK relationship chain
- recommended JOIN path for the user's objective

## PostgreSQL Safety Rails

- Use PostgreSQL dialect only.
- Never query SQLite metadata (`sqlite_master`) or use SQLite pragmas.
- Keep discovery queries read-only.
- Apply `LIMIT` when previewing row-level data.

## Error Recovery

1. `relation does not exist`:
   - Re-check schema qualification (`public.table_name`)
   - Confirm exact table name from `information_schema.tables`
2. `permission denied`:
   - Continue with accessible schemas only and report restrictions
3. Empty metadata results:
   - Expand scope beyond `public` and list all non-system schemas first

