#!/usr/bin/env python3
"""
Load Single Supabase Auth Guide to Vector Database

This script loads only the comprehensive Supabase Auth guide to test
the vector search and AI guidance system with a single, focused example.
"""

import os
import json
import logging
import asyncio
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from symmetra.vector_search import vector_search_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_supabase_auth_guide():
    """Return the comprehensive Supabase Auth guide"""
    
    return {
        "title": "Complete Next.js + Supabase Authentication System (SSR)",
        "guidance": """# Complete Next.js + Supabase Authentication System (Server-Side Rendering)

This is a production-ready authentication system using Supabase Auth with Next.js App Router, following official Supabase patterns for server-side authentication.

## 📦 Required Dependencies

```bash
npm install @supabase/supabase-js @supabase/ssr
```

## 🌍 Environment Configuration

Create `.env.local` in your project root:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-anon-key
```

## 🔧 Supabase Client Setup

### Client Component Client (`utils/supabase/client.ts`)

```typescript
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  )
}
```

### Server Component Client (`utils/supabase/server.ts`)

```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  )
}
```

## 🔄 Middleware Setup

### Main Middleware (`middleware.ts`)

```typescript
import { type NextRequest } from 'next/server'
import { updateSession } from '@/utils/supabase/middleware'

export async function middleware(request: NextRequest) {
  return await updateSession(request)
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
```

### Middleware Utils (`utils/supabase/middleware.ts`)

```typescript
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({
            request,
          })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  // IMPORTANT: Avoid writing any logic between createServerClient and
  // supabase.auth.getUser(). A simple mistake could make it very hard to debug
  // issues with users being randomly logged out.

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (
    !user &&
    !request.nextUrl.pathname.startsWith('/login') &&
    !request.nextUrl.pathname.startsWith('/auth')
  ) {
    // no user, potentially respond by redirecting the user to the login page
    const url = request.nextUrl.clone()
    url.pathname = '/login'
    return NextResponse.redirect(url)
  }

  // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're
  // creating a new response object with NextResponse.next() make sure to:
  // 1. Pass the request in it, like so:
  //    const myNewResponse = NextResponse.next({ request })
  // 2. Copy over the cookies, like so:
  //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
  // 3. Change the myNewResponse object to fit your needs, but avoid changing
  //    the cookies!
  // 4. Finally:
  //    return myNewResponse
  // If this is not done, you may be causing the browser and server to go out
  // of sync and terminate the user's session prematurely!

  return supabaseResponse
}
```

## 🔐 Authentication Pages and Actions

### Login Page (`app/login/page.tsx`)

```typescript
import { login, signup } from './actions'

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <form className="mt-8 space-y-6">
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              formAction={login}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Sign in
            </button>
            <button
              formAction={signup}
              className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Sign up
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
```

### Authentication Actions (`app/login/actions.ts`)

```typescript
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { createClient } from '@/utils/supabase/server'

export async function login(formData: FormData) {
  const supabase = await createClient()

  // Type-casting here for convenience
  // In practice, you should validate your inputs
  const data = {
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  }

  const { error } = await supabase.auth.signInWithPassword(data)

  if (error) {
    console.error('Login error:', error)
    redirect('/error')
  }

  revalidatePath('/', 'layout')
  redirect('/private')
}

export async function signup(formData: FormData) {
  const supabase = await createClient()

  // Type-casting here for convenience
  // In practice, you should validate your inputs
  const data = {
    email: formData.get('email') as string,
    password: formData.get('password') as string,
  }

  const { error } = await supabase.auth.signUp(data)

  if (error) {
    console.error('Signup error:', error)
    redirect('/error')
  }

  revalidatePath('/', 'layout')
  redirect('/private')
}

export async function signout() {
  const supabase = await createClient()
  
  const { error } = await supabase.auth.signOut()
  
  if (error) {
    console.error('Signout error:', error)
    redirect('/error')
  }

  revalidatePath('/', 'layout')
  redirect('/login')
}
```

## ✅ Email Confirmation Flow

### Confirmation Route Handler (`app/auth/confirm/route.ts`)

```typescript
import { type EmailOtpType } from '@supabase/supabase-js'
import { type NextRequest } from 'next/server'
import { createClient } from '@/utils/supabase/server'
import { redirect } from 'next/navigation'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const token_hash = searchParams.get('token_hash')
  const type = searchParams.get('type') as EmailOtpType | null
  const next = searchParams.get('next') ?? '/private'

  if (token_hash && type) {
    const supabase = await createClient()

    const { error } = await supabase.auth.verifyOtp({
      type,
      token_hash,
    })

    if (!error) {
      // redirect user to specified redirect URL or private page
      redirect(next)
    }
  }

  // redirect the user to an error page with instructions
  redirect('/error')
}
```

### Update Email Template Configuration

In your Supabase Dashboard → Auth → Templates:

**Confirm signup template:** Change `{{ .ConfirmationURL }}` to:
```
{{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=email
```

## 🔒 Protected Pages

### Private Page (`app/private/page.tsx`)

```typescript
import { redirect } from 'next/navigation'
import { createClient } from '@/utils/supabase/server'
import { signout } from '@/app/login/actions'

export default async function PrivatePage() {
  const supabase = await createClient()

  const { data, error } = await supabase.auth.getUser()

  if (error || !data?.user) {
    redirect('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome to your private page!
          </h1>
          <p className="text-gray-600 mb-6">
            Hello, {data.user.email}
          </p>
          <div className="space-y-4">
            <div className="text-sm text-gray-500">
              <p>User ID: {data.user.id}</p>
              <p>Last sign in: {data.user.last_sign_in_at}</p>
              <p>Email confirmed: {data.user.email_confirmed_at ? 'Yes' : 'No'}</p>
            </div>
            <form action={signout}>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Sign out
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
```

## 📱 Client-Side Authentication Hook

### Custom Hook (`hooks/useAuth.ts`)

```typescript
'use client'

import { useEffect, useState } from 'react'
import { User } from '@supabase/supabase-js'
import { createClient } from '@/utils/supabase/client'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    // Get initial session
    const getSession = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      setUser(session?.user ?? null)
      setLoading(false)
    }

    getSession()

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [supabase.auth])

  return {
    user,
    loading,
    signOut: () => supabase.auth.signOut(),
  }
}
```

## 🛡️ Security Best Practices

### Rate Limiting Configuration

In your Supabase Dashboard → Auth → Settings:

- **Rate Limits**: Enable rate limiting for sign-in attempts
- **Session Limits**: Configure session timeout (default 24 hours)
- **Password Requirements**: Enforce strong passwords

### Row Level Security (RLS)

```sql
-- Enable RLS on your tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Users can only access their own profile
CREATE POLICY "Users can view own profile" 
  ON profiles FOR SELECT 
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
  ON profiles FOR UPDATE 
  USING (auth.uid() = id);
```

## 🧪 Testing Authentication Flow

### Test User Registration and Login

```typescript
// __tests__/auth.test.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
)

describe('Authentication Flow', () => {
  test('should sign up new user', async () => {
    const { data, error } = await supabase.auth.signUp({
      email: 'test@example.com',
      password: 'securepassword123',
    })

    expect(error).toBeNull()
    expect(data.user).toBeDefined()
    expect(data.user?.email).toBe('test@example.com')
  })

  test('should sign in existing user', async () => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: 'test@example.com',
      password: 'securepassword123',
    })

    expect(error).toBeNull()
    expect(data.user).toBeDefined()
    expect(data.session).toBeDefined()
  })

  test('should sign out user', async () => {
    await supabase.auth.signInWithPassword({
      email: 'test@example.com',
      password: 'securepassword123',
    })

    const { error } = await supabase.auth.signOut()
    expect(error).toBeNull()

    const { data: { session } } = await supabase.auth.getSession()
    expect(session).toBeNull()
  })
})
```

## 🚀 Production Deployment Checklist

- [ ] Configure custom SMTP for email delivery
- [ ] Set up proper redirect URLs for production domain
- [ ] Enable email confirmation (recommended)
- [ ] Configure rate limiting and security settings
- [ ] Set up Row Level Security (RLS) policies
- [ ] Test email confirmation flow in production
- [ ] Configure social login providers (optional)
- [ ] Set up monitoring and logging
- [ ] Implement proper error handling and user feedback
- [ ] Test authentication flow across different browsers

## 🔗 Additional Features

### Social Login (OAuth)

```typescript
// OAuth login action
export async function loginWithGoogle() {
  const supabase = await createClient()
  
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
    },
  })

  if (error) {
    console.error('OAuth error:', error)
    redirect('/error')
  }

  redirect(data.url)
}
```

### Magic Link Authentication

```typescript
// Magic link login
export async function loginWithMagicLink(formData: FormData) {
  const supabase = await createClient()
  const email = formData.get('email') as string

  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/callback`,
    },
  })

  if (error) {
    console.error('Magic link error:', error)
    redirect('/error')
  }

  redirect('/check-email')
}
```

This implementation follows Supabase's official Next.js authentication patterns with server-side rendering, providing enterprise-grade authentication with proper security measures, email confirmation, and comprehensive error handling.""",
        "category": "security",
        "priority": "high",
        "rationale": "Complete Next.js + Supabase authentication system following official Supabase patterns for server-side rendering. Includes middleware setup, email confirmation, protected routes, social login, and production security best practices.",
        "source": ["https://supabase.com/docs/guides/auth/server-side/nextjs"],
        "loaded_at": datetime.now(timezone.utc).isoformat(),
        "last_retrieved": None
    }

async def main():
    """Load single Supabase Auth guide to vector database"""
    load_dotenv()
    
    logger.info("=" * 80)
    logger.info("LOADING SINGLE SUPABASE AUTH GUIDE")
    logger.info("=" * 80)
    
    # Check if vector search is available
    if not vector_search_engine.is_available():
        logger.error("❌ Vector search engine not available. Check Supabase configuration.")
        return
    
    # Get clients
    client = vector_search_engine._get_supabase_client()
    model = vector_search_engine._get_embedding_model()
    
    if not client or not model:
        logger.error("❌ Failed to initialize Supabase client or embedding model")
        return
    
    logger.info("✅ Vector search engine initialized successfully")
    
    # Get the Supabase Auth guide
    logger.info("\n📥 Loading Supabase Auth guide to vector database...")
    
    auth_guide = get_supabase_auth_guide()
    
    try:
        logger.info(f"   Processing: {auth_guide['title']}")
        
        # Generate embedding for the guidance content
        guidance_text = f"{auth_guide['title']} {auth_guide['guidance']}"
        embedding = model.encode(guidance_text).tolist()
        
        logger.info(f"   ├── Generated embedding (size: {len(embedding)})")
        
        # Insert rule into database with metadata
        rule_id = str(uuid.uuid4())
        result = client.table('rules').insert({
            'rule_id': rule_id,
            'title': auth_guide['title'],
            'guidance': auth_guide['guidance'],
            'category': auth_guide['category'],
            'priority': auth_guide['priority'],
            'rationale': auth_guide['rationale'],
            'embedding': json.dumps(embedding),
            'project_id': None,  # Global rule  
            'created_by': None,  # Use None since this field expects UUID
            'keywords': ['supabase', 'nextjs', 'authentication', 'auth', 'ssr', 'server-side'],
            'source': json.dumps(auth_guide.get('source', [])),
            'loaded_at': auth_guide.get('loaded_at'),
            'last_retrieved': auth_guide.get('last_retrieved')
        }).execute()
        
        if result.data:
            rule_id = result.data[0]['rule_id']
            logger.info(f"   ✅ Successfully added rule ID: {rule_id}")
        else:
            logger.error(f"   ❌ Failed to add auth guide")
            return
            
    except Exception as e:
        logger.error(f"   ❌ Error adding auth guide: {e}")
        return
    
    # Test vector search with auth-related queries
    logger.info("\n🔍 Testing vector search with auth queries...")
    
    test_queries = [
        "implement user authentication with Next.js",
        "Supabase auth server-side rendering",
        "JWT tokens and session management",
        "secure login flow with middleware"
    ]
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n   Query {i}: '{query}'")
        
        try:
            relevant_rules = vector_search_engine.search_rules(query, limit=1)
            
            if relevant_rules:
                rule = relevant_rules[0]
                logger.info(f"   ✅ Found: {rule['title']} (similarity: {rule['similarity']:.3f})")
            else:
                logger.warning(f"   ⚠️ No relevant rules found")
                
        except Exception as e:
            logger.error(f"   ❌ Search failed: {e}")
    
    # Test AI guidance integration
    logger.info("\n🤖 Testing AI guidance integration...")
    
    from symmetra.ai_guidance import guidance_engine
    
    try:
        response = guidance_engine.get_guidance(
            action="implement authentication system for Next.js app",
            context="Building a web application with Supabase backend"
        )
        
        logger.info("   ✅ AI guidance system test:")
        logger.info(f"      - Guidance items: {len(response.guidance)}")
        logger.info(f"      - Rules applied: {response.rules_applied}")
        logger.info(f"      - Complexity score: {response.complexity_score}")
        
    except Exception as e:
        logger.error(f"   ❌ AI guidance test failed: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ SINGLE SUPABASE AUTH GUIDE LOADED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info("\nDatabase now contains only the comprehensive Supabase Auth guide.")
    logger.info("Ready for testing with Claude Code!")

if __name__ == "__main__":
    asyncio.run(main())