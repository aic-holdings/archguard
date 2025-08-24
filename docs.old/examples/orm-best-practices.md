# ORM Best Practices

This guide demonstrates how to use **Drizzle ORM** effectively in AI-powered development workflows. These patterns are designed to be clear, type-safe, and easy for AI agents to understand and modify.

!!! tip "Core Principle"
    **Always use Drizzle ORM for database operations** instead of raw SQL or RPC functions. This provides type safety, better debugging, and more maintainable code.

## Why Drizzle Over Alternatives

### ✅ Advantages for AI Development

=== "Type Safety"
    ```typescript
    // ✅ Full TypeScript integration with autocomplete
    const user = await db.select().from(users).where(eq(users.id, userId));
    // TypeScript knows the exact shape of 'user'
    ```

=== "Readable Code"
    ```typescript
    // ✅ SQL-like syntax that's easy to understand
    const query = db
      .select({
        name: users.name,
        email: users.email,
        postCount: count(posts.id)
      })
      .from(users)
      .leftJoin(posts, eq(posts.authorId, users.id))
      .groupBy(users.id);
    ```

=== "Zero Runtime"
    ```typescript
    // ✅ Compiles to efficient SQL - no runtime overhead
    // Generated SQL:
    // SELECT users.name, users.email, COUNT(posts.id) as post_count
    // FROM users LEFT JOIN posts ON posts.author_id = users.id
    // GROUP BY users.id
    ```

=== "Migration Management"
    ```typescript
    // ✅ Schema changes are code-first and version controlled
    export const users = pgTable('users', {
      id: uuid('id').primaryKey().defaultRandom(),
      name: varchar('name', { length: 255 }).notNull(),
      email: varchar('email', { length: 255 }).unique().notNull(),
      createdAt: timestamp('created_at').defaultNow(),
    });
    ```

### ❌ Patterns to Avoid

!!! danger "Anti-Patterns"

    === "Raw SQL"
        ```typescript
        // ❌ Raw SQL - Hard to debug, security risks, no type safety
        const result = await supabase.rpc('execute_sql', { 
          sql_query: `SELECT * FROM charges WHERE job_id = '${jobId}'` 
        });
        // Problems: SQL injection risk, no TypeScript support, hard to refactor
        ```

    === "RPC Functions"
        ```typescript
        // ❌ RPC Functions - Black box, requires database deployments
        const result = await supabase.rpc('get_charges_breakdown', { 
          p_job_id: jobId 
        });
        // Problems: No type safety, requires DB deployment, hard to debug
        ```

    === "Basic Supabase"
        ```typescript
        // ❌ Basic Supabase - Limited type safety, complex queries get messy
        const result = await supabase
          .from('charges')
          .select('*')
          .eq('job_id', jobId);
        // Problems: Limited query building, weak typing, no relations
        ```

## Complete Setup Guide

### 1. Install Dependencies

```bash title="Install Drizzle ORM"
npm install drizzle-orm drizzle-kit postgres
npm install -D @types/pg
```

### 2. Database Configuration

```typescript title="lib/db.ts"
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

// Connection setup
const connectionString = process.env.DATABASE_URL!;
const client = postgres(connectionString);

// Create database instance
export const db = drizzle(client);
```

### 3. Schema Definition Patterns

```typescript title="lib/schema.ts"
import { pgTable, uuid, varchar, timestamp, integer, boolean, text } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

// Users table
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: varchar('name', { length: 255 }).notNull(),
  email: varchar('email', { length: 255 }).unique().notNull(),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

// Posts table
export const posts = pgTable('posts', {
  id: uuid('id').primaryKey().defaultRandom(),
  title: varchar('title', { length: 255 }).notNull(),
  content: text('content'),
  authorId: uuid('author_id').notNull().references(() => users.id),
  publishedAt: timestamp('published_at'),
  createdAt: timestamp('created_at').defaultNow(),
});

// Define relationships
export const usersRelations = relations(users, ({ many }) => ({
  posts: many(posts),
}));

export const postsRelations = relations(posts, ({ one }) => ({
  author: one(users, {
    fields: [posts.authorId],
    references: [users.id],
  }),
}));
```

## Common Query Patterns

### Basic CRUD Operations

=== "Create"
    ```typescript
    // Single insert
    const newUser = await db.insert(users).values({
      name: 'John Doe',
      email: 'john@example.com'
    }).returning();

    // Batch insert
    const newUsers = await db.insert(users).values([
      { name: 'Alice', email: 'alice@example.com' },
      { name: 'Bob', email: 'bob@example.com' }
    ]).returning();
    ```

=== "Read"
    ```typescript
    // Select with conditions
    const user = await db.select()
      .from(users)
      .where(eq(users.email, 'john@example.com'))
      .limit(1);

    // Select with joins
    const usersWithPosts = await db.select({
      id: users.id,
      name: users.name,
      email: users.email,
      postTitle: posts.title,
      postContent: posts.content
    })
    .from(users)
    .leftJoin(posts, eq(posts.authorId, users.id));
    ```

=== "Update"
    ```typescript
    // Update single record
    const updatedUser = await db.update(users)
      .set({ 
        name: 'John Smith',
        updatedAt: new Date()
      })
      .where(eq(users.id, userId))
      .returning();

    // Conditional update
    const activatedUsers = await db.update(users)
      .set({ isActive: true })
      .where(and(
        eq(users.isActive, false),
        lt(users.createdAt, new Date('2023-01-01'))
      ))
      .returning();
    ```

=== "Delete"
    ```typescript
    // Soft delete (recommended)
    const softDeleted = await db.update(users)
      .set({ 
        isActive: false,
        updatedAt: new Date()
      })
      .where(eq(users.id, userId))
      .returning();

    // Hard delete (use cautiously)
    const deleted = await db.delete(posts)
      .where(eq(posts.id, postId))
      .returning();
    ```

### Advanced Query Patterns

=== "Aggregations"
    ```typescript
    // Count and group by
    const userStats = await db.select({
      userId: users.id,
      userName: users.name,
      postCount: count(posts.id),
      latestPost: max(posts.createdAt)
    })
    .from(users)
    .leftJoin(posts, eq(posts.authorId, users.id))
    .groupBy(users.id, users.name)
    .having(gt(count(posts.id), 0));
    ```

=== "Complex Filters"
    ```typescript
    // Multiple conditions with OR/AND
    const filteredUsers = await db.select()
      .from(users)
      .where(
        and(
          eq(users.isActive, true),
          or(
            like(users.name, '%admin%'),
            like(users.email, '%@company.com')
          )
        )
      );
    ```

=== "Subqueries"
    ```typescript
    // Users with more than 5 posts
    const activeUsers = await db.select()
      .from(users)
      .where(
        exists(
          db.select()
            .from(posts)
            .where(
              and(
                eq(posts.authorId, users.id),
                gt(
                  db.select({ count: count() }).from(posts).where(eq(posts.authorId, users.id)),
                  5
                )
              )
            )
        )
      );
    ```

## Error Handling Patterns

### Transaction Management

```typescript title="Transaction example with error handling"
import { db } from './db';

export async function createUserWithPost(
  userData: { name: string; email: string },
  postData: { title: string; content: string }
) {
  try {
    return await db.transaction(async (tx) => {
      // Create user first
      const [user] = await tx.insert(users)
        .values(userData)
        .returning();

      // Create post for the user
      const [post] = await tx.insert(posts)
        .values({
          ...postData,
          authorId: user.id
        })
        .returning();

      return { user, post };
    });
  } catch (error) {
    if (error.code === '23505') { // Unique constraint violation
      throw new Error('User with this email already exists');
    }
    throw new Error('Failed to create user and post');
  }
}
```

### Validation and Error Handling

```typescript title="Input validation with Zod"
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(2).max(255),
  email: z.string().email().max(255),
});

export async function createUserSafely(input: unknown) {
  try {
    // Validate input
    const validatedInput = createUserSchema.parse(input);
    
    // Perform database operation
    const [user] = await db.insert(users)
      .values(validatedInput)
      .returning();
    
    return { success: true, user };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { 
        success: false, 
        error: 'Invalid input', 
        details: error.errors 
      };
    }
    
    return { 
      success: false, 
      error: 'Database operation failed' 
    };
  }
}
```

## Migration Management

### Schema Evolution

```typescript title="Migration example"
// drizzle/0001_initial.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

// drizzle/0002_add_posts.sql
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  content TEXT,
  author_id UUID NOT NULL REFERENCES users(id),
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now()
);
```

### Configuration

```typescript title="drizzle.config.ts"
import type { Config } from 'drizzle-kit';

export default {
  schema: './lib/schema.ts',
  out: './drizzle',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL!,
  },
  verbose: true,
  strict: true,
} satisfies Config;
```

## Performance Best Practices

### Query Optimization

```typescript title="Optimized queries"
// ✅ Use indexes effectively
const usersByEmail = await db.select()
  .from(users)
  .where(eq(users.email, email)) // Assumes index on email
  .limit(1);

// ✅ Select only needed columns
const userSummary = await db.select({
  id: users.id,
  name: users.name,
  postCount: count(posts.id)
})
.from(users)
.leftJoin(posts, eq(posts.authorId, users.id))
.groupBy(users.id, users.name);

// ✅ Use prepared statements for repeated queries
const getUserById = db.select()
  .from(users)
  .where(eq(users.id, placeholder('userId')))
  .prepare();

const user = await getUserById.execute({ userId: 'some-uuid' });
```

### Connection Pooling

```typescript title="Connection pool configuration"
import postgres from 'postgres';

const sql = postgres(connectionString, {
  max: 20,          // Maximum connections in pool
  idle_timeout: 20, // Close idle connections after 20s
  max_lifetime: 60 * 30, // Close connections after 30min
});

export const db = drizzle(sql);
```

## AI Agent Guidelines

When working with AI agents, follow these patterns:

!!! tip "AI-Friendly Patterns"

    === "Clear Naming"
        ```typescript
        // ✅ Descriptive function names
        async function getUserWithActiveSubscription(userId: string) {
          return await db.select()
            .from(users)
            .innerJoin(subscriptions, eq(subscriptions.userId, users.id))
            .where(
              and(
                eq(users.id, userId),
                eq(subscriptions.status, 'active')
              )
            );
        }
        ```

    === "Type Exports"
        ```typescript
        // ✅ Export types for AI understanding
        export type User = InferSelectModel<typeof users>;
        export type NewUser = InferInsertModel<typeof users>;
        export type Post = InferSelectModel<typeof posts>;
        export type NewPost = InferInsertModel<typeof posts>;
        ```

    === "Documented Queries"
        ```typescript
        /**
         * Retrieves users with their post statistics
         * @param isActive - Filter by user active status
         * @param minPosts - Minimum number of posts required
         */
        export async function getUsersWithPostStats(
          isActive = true, 
          minPosts = 0
        ) {
          return await db.select({
            id: users.id,
            name: users.name,
            email: users.email,
            postCount: count(posts.id),
            latestPostDate: max(posts.createdAt)
          })
          .from(users)
          .leftJoin(posts, eq(posts.authorId, users.id))
          .where(eq(users.isActive, isActive))
          .groupBy(users.id, users.name, users.email)
          .having(gte(count(posts.id), minPosts));
        }
        ```

## Common Gotchas and Solutions

!!! warning "Common Issues"

    === "Schema Sync"
        ```typescript
        // ❌ Schema and database out of sync
        // Make sure to run migrations after schema changes
        
        // ✅ Use drizzle-kit for schema management
        npx drizzle-kit generate:pg
        npx drizzle-kit push:pg
        ```

    === "Type Inference"
        ```typescript
        // ❌ Losing type information
        const users = await db.select().from(users); // any[]
        
        // ✅ Proper typing
        const users: User[] = await db.select().from(users);
        // Or use InferSelectModel
        type UserType = InferSelectModel<typeof users>;
        ```

    === "Relationship Queries"
        ```typescript
        // ❌ N+1 query problem
        for (const user of users) {
          const posts = await db.select()
            .from(posts)
            .where(eq(posts.authorId, user.id));
        }
        
        // ✅ Single query with join
        const usersWithPosts = await db.select()
          .from(users)
          .leftJoin(posts, eq(posts.authorId, users.id));
        ```

This guide provides a comprehensive foundation for using Drizzle ORM effectively in AI-powered development workflows. The patterns shown here prioritize clarity, type safety, and maintainability - making them ideal for both human developers and AI agents.