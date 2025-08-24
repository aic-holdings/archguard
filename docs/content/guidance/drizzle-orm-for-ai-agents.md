# Drizzle ORM Guidance for AI Agents

## Core Principle
**Always use Drizzle ORM for database operations instead of raw SQL or RPC functions**. This provides type safety, better debugging, and more maintainable code that AI agents can easily understand and modify.

## Why Drizzle Over Alternatives

### ✅ Advantages for AI Development
- **Type Safety**: Full TypeScript integration with autocomplete
- **Readable Code**: SQL-like syntax that's easy to understand
- **Zero Runtime**: Compiles to efficient SQL
- **Migration Management**: Schema changes are code-first
- **Debuggable**: Query building is transparent and step-by-step
- **AI-Friendly**: Predictable patterns and clear error messages

### ❌ Avoid These Patterns
```typescript
// ❌ Raw SQL - Hard to debug, security risks
const result = await supabase.rpc('execute_sql', { 
  sql_query: `SELECT * FROM charges WHERE job_id = '${jobId}'` 
});

// ❌ RPC Functions - Black box, requires database deployments
const result = await supabase.rpc('get_charges_breakdown', { p_job_id: jobId });

// ❌ Basic Supabase - Limited type safety, complex queries get messy
const result = await supabase.from('charges').select('*').eq('job_id', jobId);
```

## Setup Guide

### 1. Install Dependencies
```bash
npm install drizzle-orm drizzle-kit postgres
npm install -D @types/pg
```

### 2. Database Configuration
```typescript
// lib/db.ts
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

const connectionString = process.env.DATABASE_URL!;
const client = postgres(connectionString);
export const db = drizzle(client);
```

### 3. Schema Definition Pattern
```typescript
// schema/charges.ts
import { pgTable, uuid, text, decimal, timestamp, boolean } from 'drizzle-orm/pg-core';

export const charges = pgTable('v_charges', {
  id: uuid('id').primaryKey(),
  jobId: uuid('job_id').notNull(),
  propertyCode: text('property_code'),
  tenantCode: text('tenant_code'),
  totalCharges: decimal('total_charges').notNull(),
  yardiCharges: decimal('yardi_charges'),
  utilityCharges: decimal('utility_charges'),
  agingCharges: decimal('aging_charges'),
  prepayments: decimal('prepayments'),
  occupancyStatus: text('occupancy_status'),
  chargeCode: text('charge_code'),
  unitNumber: text('unit_number'),
  chargeDate: timestamp('charge_date'),
  createdAt: timestamp('created_at').defaultNow(),
  deletedAt: timestamp('deleted_at')
});

// Export type for use in API routes
export type Charge = typeof charges.$inferSelect;
export type NewCharge = typeof charges.$inferInsert;
```

## Core Patterns for API Endpoints

### 1. Basic Query with Filtering
```typescript
// api/analytics/charges/route.ts
import { db } from '@/lib/db';
import { charges } from '@/schema/charges';
import { eq, and, isNull, desc, sum, count } from 'drizzle-orm';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const jobId = searchParams.get('job_id');
  
  if (!jobId) {
    return NextResponse.json({ error: 'job_id required' }, { status: 400 });
  }

  try {
    // Build conditions array
    const conditions = [
      eq(charges.jobId, jobId),
      isNull(charges.deletedAt) // Always filter soft deletes
    ];

    // Add optional filters
    const propertyFilter = searchParams.get('property');
    if (propertyFilter && propertyFilter !== 'all') {
      conditions.push(eq(charges.propertyCode, propertyFilter));
    }

    const statusFilter = searchParams.get('status');
    if (statusFilter && statusFilter !== 'all') {
      conditions.push(eq(charges.occupancyStatus, statusFilter));
    }

    // Execute query
    const result = await db
      .select({
        propertyCode: charges.propertyCode,
        tenantCount: count(),
        totalCharges: sum(charges.totalCharges),
        yardiTotal: sum(charges.yardiCharges),
        utilityTotal: sum(charges.utilityCharges)
      })
      .from(charges)
      .where(and(...conditions))
      .groupBy(charges.propertyCode)
      .orderBy(desc(sum(charges.totalCharges)));

    return NextResponse.json({ 
      success: true, 
      data: result,
      jobId 
    });

  } catch (error) {
    console.error('Database query failed:', error);
    return NextResponse.json({ 
      error: 'Failed to fetch charges data' 
    }, { status: 500 });
  }
}
```

### 2. Complex Aggregations
```typescript
// Multiple aggregations in parallel
const [summary, propertyBreakdown, categoryBreakdown] = await Promise.all([
  // Summary totals
  db
    .select({
      totalCharges: sum(charges.totalCharges),
      tenantCount: count(),
      avgCharges: sql<number>`AVG(${charges.totalCharges})`
    })
    .from(charges)
    .where(and(...baseConditions)),

  // Property breakdown
  db
    .select({
      propertyCode: charges.propertyCode,
      tenantCount: count(),
      totalCharges: sum(charges.totalCharges)
    })
    .from(charges)
    .where(and(...baseConditions))
    .groupBy(charges.propertyCode)
    .orderBy(desc(sum(charges.totalCharges))),

  // Category breakdown
  db
    .select({
      chargeCode: charges.chargeCode,
      count: count(),
      total: sum(charges.totalCharges)
    })
    .from(charges)
    .where(and(...baseConditions))
    .groupBy(charges.chargeCode)
]);
```

### 3. Pagination Pattern
```typescript
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get('page') || '1');
  const limit = parseInt(searchParams.get('limit') || '50');
  const offset = (page - 1) * limit;

  const [data, totalCount] = await Promise.all([
    // Get paginated data
    db
      .select()
      .from(charges)
      .where(and(...conditions))
      .limit(limit)
      .offset(offset)
      .orderBy(desc(charges.createdAt)),

    // Get total count for pagination
    db
      .select({ count: count() })
      .from(charges)
      .where(and(...conditions))
  ]);

  return NextResponse.json({
    success: true,
    data,
    pagination: {
      page,
      limit,
      total: totalCount[0].count,
      pages: Math.ceil(totalCount[0].count / limit)
    }
  });
}
```

### 4. Relationships and Joins
```typescript
// schema/projects.ts
export const projects = pgTable('projects', {
  id: uuid('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description')
});

// API route with joins
const result = await db
  .select({
    // Charge fields
    chargeId: charges.id,
    totalCharges: charges.totalCharges,
    propertyCode: charges.propertyCode,
    // Project fields
    projectName: projects.name,
    projectDescription: projects.description
  })
  .from(charges)
  .leftJoin(projects, eq(charges.jobId, projects.id))
  .where(and(...conditions));
```

## Error Handling Patterns

### 1. Consistent Error Structure
```typescript
// lib/api-response.ts
export function createErrorResponse(message: string, status: number = 500) {
  return NextResponse.json({ 
    success: false, 
    error: message 
  }, { status });
}

export function createSuccessResponse(data: any, meta?: any) {
  return NextResponse.json({ 
    success: true, 
    data,
    ...meta 
  });
}
```

### 2. Query Error Handling
```typescript
try {
  const result = await db.select().from(charges).where(eq(charges.jobId, jobId));
  return createSuccessResponse(result);
} catch (error) {
  console.error('Database query failed:', error);
  
  // Handle specific error types
  if (error.code === '23505') { // Unique constraint violation
    return createErrorResponse('Duplicate entry found', 409);
  }
  
  if (error.code === '23503') { // Foreign key violation
    return createErrorResponse('Referenced record not found', 400);
  }
  
  return createErrorResponse('Database operation failed', 500);
}
```

## Migration Management

### 1. Schema Changes
```typescript
// drizzle.config.ts
import type { Config } from 'drizzle-kit';

export default {
  schema: './schema/*',
  out: './migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  }
} satisfies Config;
```

### 2. Generate and Run Migrations
```bash
# Generate migration from schema changes
npx drizzle-kit generate:pg

# Apply migrations
npx drizzle-kit push:pg
```

## Performance Optimization

### 1. Efficient Queries
```typescript
// ✅ GOOD: Select only needed fields
const result = await db
  .select({
    id: charges.id,
    total: charges.totalCharges,
    property: charges.propertyCode
  })
  .from(charges)
  .where(eq(charges.jobId, jobId));

// ❌ AVOID: Select all fields when not needed
const result = await db.select().from(charges);
```

### 2. Batch Operations
```typescript
// ✅ GOOD: Batch inserts
await db.insert(charges).values([
  { jobId, propertyCode: 'PROP1', totalCharges: '100.00' },
  { jobId, propertyCode: 'PROP2', totalCharges: '200.00' }
]);

// ❌ AVOID: Individual inserts in loop
for (const charge of chargeData) {
  await db.insert(charges).values(charge);
}
```

## Testing Patterns

### 1. Query Testing
```typescript
// __tests__/charges.test.ts
import { db } from '@/lib/db';
import { charges } from '@/schema/charges';

describe('Charges API', () => {
  test('should filter charges by property', async () => {
    const result = await db
      .select()
      .from(charges)
      .where(eq(charges.propertyCode, 'TEST_PROPERTY'));
    
    expect(result).toBeDefined();
    expect(result.every(charge => charge.propertyCode === 'TEST_PROPERTY')).toBe(true);
  });
});
```

## AI Decision Tree

When building API endpoints, follow this decision tree:

1. **Need to query database?** → Use Drizzle ORM
2. **Simple CRUD?** → Use basic select/insert/update/delete
3. **Complex filtering?** → Build conditions array with `and(...conditions)`
4. **Aggregations needed?** → Use `sum()`, `count()`, `avg()` functions
5. **Multiple queries?** → Use `Promise.all()` for parallel execution
6. **Relationships?** → Use `leftJoin()` or `innerJoin()`
7. **Large datasets?** → Implement pagination pattern
8. **Schema changes needed?** → Update schema file, generate migration

## Common Patterns Cheat Sheet

```typescript
// Filtering
const conditions = [eq(table.field, value)];
if (filter) conditions.push(eq(table.filterField, filter));
const result = await db.select().from(table).where(and(...conditions));

// Aggregation
const summary = await db
  .select({ total: sum(table.amount), count: count() })
  .from(table)
  .where(condition);

// Pagination
const data = await db.select().from(table).limit(50).offset(page * 50);

// Sorting
const sorted = await db.select().from(table).orderBy(desc(table.createdAt));

// Soft delete filter
const active = await db.select().from(table).where(isNull(table.deletedAt));
```

This guidance ensures AI agents build consistent, type-safe, and maintainable database operations while avoiding the pitfalls of raw SQL and RPC functions.