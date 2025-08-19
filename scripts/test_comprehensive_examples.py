#!/usr/bin/env python3
"""
Test Script: 3 Comprehensive Code Examples with Full Vector Pipeline

This script:
1. Adds 3 detailed implementation examples to Supabase vector database  
2. Generates embeddings for each example
3. Stores them with proper metadata
4. Tests retrieval through vector search
5. Validates the complete pipeline works

Run this to prove the vector search system can handle comprehensive guides.
"""

import os
import json
import logging
import asyncio
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from symmetra.vector_search import vector_search_engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_comprehensive_examples() -> List[Dict[str, Any]]:
    """Return 3 comprehensive, detailed code examples"""
    
    return [
        {
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
        },
        
        {
            "title": "Complete FastAPI Authentication System with JWT and Rate Limiting",
            "guidance": """# Complete FastAPI Authentication System

## 🔒 Password Security Implementation

```python
from passlib.context import CryptContext
import secrets
import hashlib

class PasswordSecurity:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def generate_salt(self) -> str:
        \"\"\"Generate cryptographically secure salt\"\"\"
        return secrets.token_hex(32)
    
    def hash_password(self, password: str, salt: str) -> str:
        \"\"\"Hash password with salt using bcrypt\"\"\"
        salted_password = password + salt
        return self.pwd_context.hash(salted_password)
    
    def verify_password(self, password: str, salt: str, hashed: str) -> bool:
        \"\"\"Verify password against hash (constant time)\"\"\"
        salted_password = password + salt
        return self.pwd_context.verify(salted_password, hashed)

password_security = PasswordSecurity()
```

## 🎟️ JWT Token Management

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional, Dict, Any
import secrets

class TokenManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 15
        self.REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        \"\"\"Create JWT access token\"\"\"
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "jti": secrets.token_urlsafe(32)
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        \"\"\"Create JWT refresh token\"\"\"
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            "exp": expire,
            "type": "refresh", 
            "jti": secrets.token_urlsafe(32)
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
        \"\"\"Verify and decode JWT token\"\"\"
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != expected_type:
                return None
            return payload
        except JWTError:
            return None

token_manager = TokenManager(os.getenv("SECRET_KEY", "your-secret-key"))
```

## 🛡️ Rate Limiting with Redis

```python
import redis
import time
from functools import wraps
from fastapi import HTTPException, Request

class RateLimiter:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
    
    def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        \"\"\"Check if request should be rate limited\"\"\"
        current_time = int(time.time())
        pipeline = self.redis_client.pipeline()
        
        # Sliding window: remove old entries
        pipeline.zremrangebyscore(key, 0, current_time - window)
        # Count current requests
        pipeline.zcard(key)
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        # Set expiry
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_requests = results[1]
        
        return current_requests >= limit

rate_limiter = RateLimiter()

def rate_limit_auth(requests_per_minute: int = 5):
    \"\"\"Rate limiting decorator for auth endpoints\"\"\"
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            key = f"auth_rate_limit:{client_ip}"
            
            if rate_limiter.is_rate_limited(key, requests_per_minute, 60):
                raise HTTPException(
                    status_code=429,
                    detail="Too many authentication attempts. Try again later."
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

## 🔐 Complete FastAPI Authentication Routes

```python
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import asyncpg
from datetime import datetime
import hashlib

app = FastAPI(title="Secure Authentication API")
security = HTTPBearer()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Database connection (implement your connection logic)
async def get_db():
    # Return your database connection
    pass

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    \"\"\"Get current user from JWT token\"\"\"
    token = credentials.credentials
    payload = token_manager.verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload["sub"]  # user_id

@app.post("/auth/register", response_model=TokenResponse)
@rate_limit_auth(requests_per_minute=3)
async def register(user_data: UserRegistration, request: Request, db = Depends(get_db)):
    \"\"\"Register new user with comprehensive validation\"\"\"
    
    # Check if user exists
    existing_user = await db.fetchrow(
        "SELECT id FROM users WHERE email = $1", user_data.email
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Password strength validation (implement as needed)
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Hash password with salt
    salt = password_security.generate_salt()
    password_hash = password_security.hash_password(user_data.password, salt)
    
    # Create user
    user_id = await db.fetchval(\"\"\"
        INSERT INTO users (email, password_hash, salt)
        VALUES ($1, $2, $3)
        RETURNING id
    \"\"\", user_data.email, password_hash, salt)
    
    # Generate tokens
    access_token = token_manager.create_access_token({"sub": str(user_id)})
    refresh_token = token_manager.create_refresh_token({"sub": str(user_id)})
    
    # Store refresh token
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    await db.execute(\"\"\"
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, NOW() + INTERVAL '30 days')
    \"\"\", user_id, refresh_token_hash)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@app.post("/auth/login", response_model=TokenResponse)
@rate_limit_auth(requests_per_minute=5)
async def login(user_data: UserLogin, request: Request, db = Depends(get_db)):
    \"\"\"Login with account lockout protection\"\"\"
    
    # Get user with current timestamp check for lockout
    user = await db.fetchrow(\"\"\"
        SELECT id, email, password_hash, salt, failed_login_attempts, account_locked_until
        FROM users 
        WHERE email = $1 AND is_active = true
    \"\"\", user_data.email)
    
    if not user:
        # Constant time delay to prevent user enumeration
        await asyncio.sleep(0.1)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check account lockout
    if user['account_locked_until'] and user['account_locked_until'] > datetime.utcnow():
        remaining_lockout = user['account_locked_until'] - datetime.utcnow()
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked. Try again in {remaining_lockout.seconds} seconds."
        )
    
    # Verify password
    if not password_security.verify_password(user_data.password, user['salt'], user['password_hash']):
        # Increment failed attempts
        failed_attempts = user['failed_login_attempts'] + 1
        lockout_time = None
        
        if failed_attempts >= 5:
            lockout_time = datetime.utcnow() + timedelta(minutes=15)
        
        await db.execute(\"\"\"
            UPDATE users 
            SET failed_login_attempts = $1, account_locked_until = $2
            WHERE id = $3
        \"\"\", failed_attempts, lockout_time, user['id'])
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Successful login - reset failed attempts
    await db.execute(\"\"\"
        UPDATE users 
        SET failed_login_attempts = 0, account_locked_until = NULL
        WHERE id = $1
    \"\"\", user['id'])
    
    # Generate tokens
    access_token = token_manager.create_access_token({"sub": str(user['id'])})
    refresh_token = token_manager.create_refresh_token({"sub": str(user['id'])})
    
    # Store refresh token
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    await db.execute(\"\"\"
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, NOW() + INTERVAL '30 days')
    \"\"\", user['id'], refresh_token_hash)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@app.get("/auth/me")
async def get_current_user_info(current_user: str = Depends(get_current_user), db = Depends(get_db)):
    \"\"\"Get current user information\"\"\"
    user = await db.fetchrow(
        "SELECT id, email, created_at FROM users WHERE id = $1",
        current_user
    )
    return {"user_id": user['id'], "email": user['email'], "created_at": user['created_at']}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🧪 Testing the Authentication System

```python
import pytest
import httpx
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_user_registration(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "secure_password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_user_login(client):
    # Register first
    client.post("/auth/register", json={
        "email": "login@example.com", 
        "password": "secure_password123"
    })
    
    # Then login
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "secure_password123"
    })
    assert response.status_code == 200

def test_rate_limiting(client):
    for _ in range(6):  # Exceed rate limit
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrong_password"
        })
    
    assert response.status_code == 429
```

## 🚀 Production Deployment Checklist

- [ ] Use environment variables for all secrets
- [ ] Set up Redis cluster for rate limiting
- [ ] Configure PostgreSQL with proper connection pooling
- [ ] Enable HTTPS with proper SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure CORS for your frontend domain
- [ ] Set up automated backups for user data
- [ ] Implement email verification flow
- [ ] Add 2FA support for sensitive accounts
- [ ] Set up security monitoring and alerts

This implementation provides enterprise-grade authentication with proper security measures, rate limiting, and comprehensive error handling.""",
            "category": "security",  # Valid enum value
            "priority": "high",
            "rationale": "Complete production-ready authentication system with JWT, rate limiting, password security, account lockout protection, and comprehensive error handling. Includes database schema, implementation code, testing, and deployment checklist.",
            "source": ["https://fastapi.tiangolo.com/tutorial/security/", "https://passlib.readthedocs.io/en/stable/"],
            "loaded_at": datetime.now(timezone.utc).isoformat(),
            "last_retrieved": None
        },
        
        {
            "title": "High-Performance Database Connection Pooling and Query Optimization",
            "guidance": """# High-Performance Database Architecture with Connection Pooling

This guide covers enterprise-grade database patterns including connection pooling, query optimization, and monitoring for production applications.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Application   │────│  Connection Pool │────│   PostgreSQL    │
│    Instances    │    │   (PgBouncer)    │    │    Database     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        ├── Read Replicas ────────┼────────────────────────┘
        └── Monitoring ───────────┘
```

## 📦 Required Setup

```bash
# Install dependencies
pip install asyncpg sqlalchemy[asyncio] alembic redis prometheus_client

# Install PgBouncer (Ubuntu/Debian)
sudo apt install pgbouncer

# Install PostgreSQL monitoring
pip install psycopg2-binary pg_activity
```

## 🔧 PgBouncer Configuration

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
production_db = host=localhost port=5432 dbname=myapp user=app_user password=secure_password

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Connection pooling settings
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
max_db_connections = 30

# Performance tuning
server_reset_query = DISCARD ALL
server_check_delay = 30
server_check_query = SELECT 1

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1

# Security
admin_users = pgbouncer_admin
stats_users = pgbouncer_stats
```

## 🗄️ Optimized Database Schema with Indexes

```sql
-- Users table with proper indexing
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Orders table with partitioning for large datasets
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) NOT NULL,
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE orders_2024_02 PARTITION OF orders  
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Strategic indexes for performance
CREATE INDEX idx_users_email_active ON users(email) WHERE is_active = true;
CREATE INDEX idx_users_username_lower ON users(lower(username));
CREATE INDEX idx_users_last_login ON users(last_login) WHERE last_login IS NOT NULL;

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index for active orders only
CREATE INDEX idx_orders_active ON orders(created_at DESC) 
    WHERE status IN ('pending', 'processing');

-- JSONB indexes for flexible data
ALTER TABLE users ADD COLUMN metadata JSONB;
CREATE INDEX idx_users_metadata_gin ON users USING gin(metadata);
```

## 🚀 High-Performance Connection Pool Implementation

```python
import asyncpg
import asyncio
from typing import Optional, Any, List, Dict
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
import time
import weakref

@dataclass
class ConnectionPoolConfig:
    dsn: str
    min_size: int = 10
    max_size: int = 100
    max_queries: int = 50000
    max_inactive_connection_lifetime: float = 300.0
    command_timeout: float = 60.0
    server_settings: Optional[Dict[str, str]] = None

class DatabaseConnectionPool:
    def __init__(self, config: ConnectionPoolConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        \"\"\"Initialize connection pool with optimized settings\"\"\"
        try:
            self.pool = await asyncpg.create_pool(
                self.config.dsn,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                max_queries=self.config.max_queries,
                max_inactive_connection_lifetime=self.config.max_inactive_connection_lifetime,
                command_timeout=self.config.command_timeout,
                server_settings=self.config.server_settings or {
                    'application_name': 'myapp_api',
                    'tcp_keepalives_idle': '600',
                    'tcp_keepalives_interval': '30',
                    'tcp_keepalives_count': '3',
                }
            )
            self.logger.info(f"Database pool initialized with {self.config.min_size}-{self.config.max_size} connections")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self):
        \"\"\"Gracefully close all connections\"\"\"
        if self.pool:
            await self.pool.close()
            self.logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        \"\"\"Get database connection from pool\"\"\"
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        start_time = time.time()
        async with self.pool.acquire() as connection:
            try:
                yield connection
            finally:
                duration = time.time() - start_time
                self.logger.debug(f"Connection used for {duration:.3f}s")
    
    async def execute(self, query: str, *args) -> str:
        \"\"\"Execute a query and return status\"\"\"
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        \"\"\"Fetch multiple rows\"\"\"
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        \"\"\"Fetch single row\"\"\"
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        \"\"\"Fetch single value\"\"\"
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)

# Global pool instance
db_pool = None

async def initialize_database():
    \"\"\"Initialize database connection pool\"\"\"
    global db_pool
    config = ConnectionPoolConfig(
        dsn="postgresql://user:password@localhost:6432/myapp",  # via PgBouncer
        min_size=10,
        max_size=50,
    )
    db_pool = DatabaseConnectionPool(config)
    await db_pool.initialize()

def get_db_pool() -> DatabaseConnectionPool:
    \"\"\"Get database pool instance\"\"\"
    if not db_pool:
        raise RuntimeError("Database not initialized")
    return db_pool
```

## 📊 Query Optimization and Analysis

```python
import asyncio
from typing import Dict, Any, List
import time
from dataclasses import dataclass

@dataclass
class QueryMetrics:
    query: str
    duration: float
    rows_affected: int
    timestamp: float

class QueryOptimizer:
    def __init__(self, db_pool: DatabaseConnectionPool):
        self.db_pool = db_pool
        self.query_metrics: List[QueryMetrics] = []
        self.slow_query_threshold = 1.0  # seconds
        self.logger = logging.getLogger(__name__)
    
    async def execute_with_metrics(self, query: str, *args) -> Any:
        \"\"\"Execute query with performance monitoring\"\"\"
        start_time = time.time()
        
        async with self.db_pool.get_connection() as conn:
            # Enable query analysis
            await conn.execute("SET log_statement_stats = on")
            
            result = await conn.fetch(query, *args)
            
            duration = time.time() - start_time
            
            # Log slow queries
            if duration > self.slow_query_threshold:
                explain_result = await conn.fetch(f"EXPLAIN ANALYZE {query}", *args)
                self.logger.warning(
                    f"Slow query detected ({duration:.3f}s): {query[:100]}..."
                )
                self.logger.warning(f"Execution plan: {explain_result}")
            
            # Store metrics
            self.query_metrics.append(QueryMetrics(
                query=query,
                duration=duration,
                rows_affected=len(result),
                timestamp=time.time()
            ))
            
            return result
    
    async def analyze_table_stats(self, table_name: str) -> Dict[str, Any]:
        \"\"\"Get comprehensive table statistics\"\"\"
        stats_query = \"\"\"
        SELECT 
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation,
            null_frac
        FROM pg_stats 
        WHERE tablename = $1
        ORDER BY attname;
        \"\"\"
        
        size_query = \"\"\"
        SELECT 
            pg_size_pretty(pg_total_relation_size($1)) as total_size,
            pg_size_pretty(pg_relation_size($1)) as table_size,
            pg_size_pretty(pg_total_relation_size($1) - pg_relation_size($1)) as index_size
        \"\"\"
        
        async with self.db_pool.get_connection() as conn:
            stats = await conn.fetch(stats_query, table_name)
            sizes = await conn.fetchrow(size_query, table_name)
            
        return {
            "column_stats": [dict(row) for row in stats],
            "sizes": dict(sizes) if sizes else {},
            "analysis_timestamp": time.time()
        }
    
    def get_slow_queries(self, limit: int = 10) -> List[QueryMetrics]:
        \"\"\"Get slowest queries\"\"\"
        return sorted(
            self.query_metrics,
            key=lambda x: x.duration,
            reverse=True
        )[:limit]

# Example usage with optimized queries
class UserRepository:
    def __init__(self, db_pool: DatabaseConnectionPool):
        self.db_pool = db_pool
        self.optimizer = QueryOptimizer(db_pool)
    
    async def find_active_users_by_domain(self, email_domain: str) -> List[Dict[str, Any]]:
        \"\"\"Optimized query with proper indexing\"\"\"
        query = \"\"\"
        SELECT id, email, username, last_login
        FROM users 
        WHERE email LIKE $1 
        AND is_active = true
        ORDER BY last_login DESC NULLS LAST
        LIMIT 100
        \"\"\"
        
        result = await self.optimizer.execute_with_metrics(
            query, f"%@{email_domain}"
        )
        return [dict(row) for row in result]
    
    async def get_user_order_summary(self, user_id: str) -> Dict[str, Any]:
        \"\"\"Optimized aggregation query\"\"\"
        query = \"\"\"
        SELECT 
            u.email,
            u.username,
            COUNT(o.id) as total_orders,
            COALESCE(SUM(o.total_amount), 0) as total_spent,
            MAX(o.created_at) as last_order_date
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.id = $1
        GROUP BY u.id, u.email, u.username
        \"\"\"
        
        result = await self.optimizer.execute_with_metrics(query, user_id)
        return dict(result[0]) if result else {}

# Batch operations for better performance
class BatchOperations:
    def __init__(self, db_pool: DatabaseConnectionPool):
        self.db_pool = db_pool
    
    async def bulk_insert_users(self, users: List[Dict[str, Any]]) -> None:
        \"\"\"Efficient bulk insert using COPY\"\"\"
        async with self.db_pool.get_connection() as conn:
            # Prepare data for COPY
            columns = ['email', 'username', 'created_at']
            
            await conn.copy_records_to_table(
                'users',
                records=[(u['email'], u['username'], u.get('created_at', 'NOW()')) for u in users],
                columns=columns
            )
    
    async def bulk_update_user_activity(self, user_activities: Dict[str, Any]) -> None:
        \"\"\"Efficient bulk update using temporary table\"\"\"
        async with self.db_pool.get_connection() as conn:
            # Create temporary table
            await conn.execute(\"\"\"
                CREATE TEMP TABLE temp_user_updates (
                    user_id UUID,
                    last_login TIMESTAMP
                )
            \"\"\")
            
            # Bulk insert to temp table
            await conn.executemany(
                "INSERT INTO temp_user_updates VALUES ($1, $2)",
                [(uid, login_time) for uid, login_time in user_activities.items()]
            )
            
            # Single UPDATE with JOIN
            await conn.execute(\"\"\"
                UPDATE users 
                SET last_login = temp_user_updates.last_login
                FROM temp_user_updates
                WHERE users.id = temp_user_updates.user_id
            \"\"\")
```

## 📈 Monitoring and Health Checks

```python
from prometheus_client import Counter, Histogram, Gauge
import psutil

# Metrics collection
db_queries_total = Counter('db_queries_total', 'Total database queries', ['table', 'operation'])
db_query_duration = Histogram('db_query_duration_seconds', 'Query execution time')
db_connections_active = Gauge('db_connections_active', 'Active database connections')

class DatabaseMonitoring:
    def __init__(self, db_pool: DatabaseConnectionPool):
        self.db_pool = db_pool
        self.logger = logging.getLogger(__name__)
    
    async def health_check(self) -> Dict[str, Any]:
        \"\"\"Comprehensive database health check\"\"\"
        try:
            start_time = time.time()
            
            # Test basic connectivity
            async with self.db_pool.get_connection() as conn:
                await conn.fetchval("SELECT 1")
                
            response_time = time.time() - start_time
            
            # Get pool statistics
            pool_stats = {
                "size": self.db_pool.pool.get_size(),
                "max_size": self.db_pool.pool.get_max_size(),
                "min_size": self.db_pool.pool.get_min_size(),
                "idle_connections": self.db_pool.pool.get_idle_size(),
            }
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "pool_stats": pool_stats,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def get_active_queries(self) -> List[Dict[str, Any]]:
        \"\"\"Get currently running queries\"\"\"
        query = \"\"\"
        SELECT 
            pid,
            usename,
            application_name,
            client_addr,
            query_start,
            state,
            query
        FROM pg_stat_activity 
        WHERE state = 'active'
        AND query NOT LIKE '%pg_stat_activity%'
        ORDER BY query_start
        \"\"\"
        
        async with self.db_pool.get_connection() as conn:
            result = await conn.fetch(query)
            
        return [dict(row) for row in result]
```

This implementation provides enterprise-grade database performance with proper connection pooling, query optimization, monitoring, and health checks for production applications.""",
            "category": "performance",  # Changed from "database" to valid enum value "performance"
            "priority": "high", 
            "rationale": "Enterprise-grade database architecture with connection pooling, query optimization, monitoring, and batch operations. Critical for applications that need high performance and reliability at scale.",
            "source": ["https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html", "https://magicstack.github.io/asyncpg/current/"],
            "loaded_at": datetime.now(timezone.utc).isoformat(),
            "last_retrieved": None
        },
        
        {
            "title": "Production-Ready Redis Caching Architecture with Fallback Strategies",
            "guidance": """# Production Redis Caching Architecture

Complete caching implementation with Redis clustering, fallback strategies, cache warming, and monitoring for high-performance applications.

## 🏗️ Cache Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Application   │────│   Cache Layer    │────│   Primary DB    │
│    Services     │    │  (Redis Cluster) │    │  (PostgreSQL)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        ├── Circuit Breaker ──────┼────────────────────────┘
        ├── Cache Warming ────────┤
        └── Monitoring ───────────┘
```

## 📦 Redis Cluster Setup

```bash
# Install Redis
sudo apt install redis-server redis-tools

# Redis Cluster Configuration (6 nodes: 3 masters + 3 replicas)
# redis-cluster-config/
├── redis-7000.conf
├── redis-7001.conf
├── redis-7002.conf
├── redis-7003.conf
├── redis-7004.conf
└── redis-7005.conf
```

```ini
# redis-7000.conf (adjust port for each node)
port 7000
cluster-enabled yes
cluster-config-file nodes-7000.conf
cluster-node-timeout 5000
appendonly yes
appendfilename "appendonly-7000.aof"

# Performance optimizations
maxmemory 2gb
maxmemory-policy allkeys-lru
tcp-keepalive 60
tcp-backlog 511

# Security
requirepass your_strong_password
masterauth your_strong_password
```

## 🚀 High-Performance Cache Client Implementation

```python
import redis.asyncio as redis
import json
import asyncio
import time
import logging
import hashlib
from typing import Any, Optional, Dict, List, Union, Callable
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from enum import Enum
import pickle
import zlib

class CacheStrategy(Enum):
    CACHE_ASIDE = "cache_aside"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    REFRESH_AHEAD = "refresh_ahead"

@dataclass
class CacheConfig:
    redis_url: str = "redis://localhost:6379"
    cluster_nodes: List[str] = None
    default_ttl: int = 3600  # 1 hour
    max_connections: int = 100
    retry_on_timeout: bool = True
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    health_check_interval: int = 30

class CacheSerializationError(Exception):
    pass

class CacheConnectionError(Exception):
    pass

class ProductionCacheClient:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.cluster_client: Optional[redis.RedisCluster] = None
        self.logger = logging.getLogger(__name__)
        self._circuit_breaker_failures = 0
        self._circuit_breaker_threshold = 5
        self._circuit_breaker_reset_time = 60
        self._last_failure_time = 0
        
    async def initialize(self):
        \"\"\"Initialize Redis connection with cluster support\"\"\"
        try:
            if self.config.cluster_nodes:
                # Redis Cluster setup
                startup_nodes = [
                    redis.RedisCluster.RedisNode(node.split(':')[0], int(node.split(':')[1]))
                    for node in self.config.cluster_nodes
                ]
                
                self.cluster_client = redis.RedisCluster(
                    startup_nodes=startup_nodes,
                    decode_responses=False,  # Handle binary data
                    skip_full_coverage_check=True,
                    max_connections=self.config.max_connections,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    retry_on_timeout=self.config.retry_on_timeout,
                )
                
                # Test cluster connection
                await self.cluster_client.ping()
                self.logger.info(f"Connected to Redis cluster with {len(self.config.cluster_nodes)} nodes")
                
            else:
                # Single Redis instance
                self.redis_client = redis.from_url(
                    self.config.redis_url,
                    max_connections=self.config.max_connections,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    retry_on_timeout=self.config.retry_on_timeout,
                    decode_responses=False,
                )
                
                await self.redis_client.ping()
                self.logger.info("Connected to Redis server")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis: {e}")
            raise CacheConnectionError(f"Redis initialization failed: {e}")
    
    def _get_client(self) -> Union[redis.Redis, redis.RedisCluster]:
        \"\"\"Get appropriate Redis client\"\"\"
        return self.cluster_client if self.cluster_client else self.redis_client
    
    def _is_circuit_breaker_open(self) -> bool:
        \"\"\"Check if circuit breaker is open\"\"\"
        if self._circuit_breaker_failures < self._circuit_breaker_threshold:
            return False
            
        time_since_last_failure = time.time() - self._last_failure_time
        if time_since_last_failure > self._circuit_breaker_reset_time:
            self._circuit_breaker_failures = 0
            return False
            
        return True
    
    def _record_failure(self):
        \"\"\"Record circuit breaker failure\"\"\"
        self._circuit_breaker_failures += 1
        self._last_failure_time = time.time()
    
    def _serialize_data(self, data: Any) -> bytes:
        \"\"\"Serialize data with compression\"\"\"
        try:
            # Use pickle for Python objects, compress for large data
            serialized = pickle.dumps(data)
            
            # Compress if data is large (> 1KB)
            if len(serialized) > 1024:
                serialized = zlib.compress(serialized)
                return b'compressed:' + serialized
            
            return b'pickle:' + serialized
            
        except Exception as e:
            raise CacheSerializationError(f"Serialization failed: {e}")
    
    def _deserialize_data(self, data: bytes) -> Any:
        \"\"\"Deserialize data with decompression\"\"\"
        try:
            if data.startswith(b'compressed:'):
                decompressed = zlib.decompress(data[11:])  # Remove 'compressed:' prefix
                return pickle.loads(decompressed)
            elif data.startswith(b'pickle:'):
                return pickle.loads(data[7:])  # Remove 'pickle:' prefix
            else:
                # Fallback for plain JSON (backward compatibility)
                return json.loads(data.decode('utf-8'))
                
        except Exception as e:
            raise CacheSerializationError(f"Deserialization failed: {e}")
    
    def _generate_cache_key(self, key: str, prefix: str = "app") -> str:
        \"\"\"Generate consistent cache key with prefix\"\"\"
        return f"{prefix}:{key}"
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        prefix: str = "app"
    ) -> bool:
        \"\"\"Set cache value with automatic serialization\"\"\"
        if self._is_circuit_breaker_open():
            self.logger.warning("Cache circuit breaker is open, skipping set")
            return False
        
        try:
            client = self._get_client()
            cache_key = self._generate_cache_key(key, prefix)
            serialized_value = self._serialize_data(value)
            ttl = ttl or self.config.default_ttl
            
            result = await client.set(cache_key, serialized_value, ex=ttl)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Cache set failed for key {key}: {e}")
            self._record_failure()
            return False
    
    async def get(self, key: str, prefix: str = "app") -> Optional[Any]:
        \"\"\"Get cache value with automatic deserialization\"\"\"
        if self._is_circuit_breaker_open():
            self.logger.warning("Cache circuit breaker is open, skipping get")
            return None
        
        try:
            client = self._get_client()
            cache_key = self._generate_cache_key(key, prefix)
            
            data = await client.get(cache_key)
            if data is None:
                return None
                
            return self._deserialize_data(data)
            
        except Exception as e:
            self.logger.error(f"Cache get failed for key {key}: {e}")
            self._record_failure()
            return None
    
    async def mget(self, keys: List[str], prefix: str = "app") -> Dict[str, Any]:
        \"\"\"Get multiple cache values\"\"\"
        if self._is_circuit_breaker_open():
            return {}
        
        try:
            client = self._get_client()
            cache_keys = [self._generate_cache_key(key, prefix) for key in keys]
            
            values = await client.mget(cache_keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = self._deserialize_data(value)
                    except CacheSerializationError:
                        self.logger.warning(f"Failed to deserialize cached value for key: {key}")
                        
            return result
            
        except Exception as e:
            self.logger.error(f"Cache mget failed: {e}")
            self._record_failure()
            return {}
    
    async def delete(self, key: str, prefix: str = "app") -> bool:
        \"\"\"Delete cache value\"\"\"
        try:
            client = self._get_client()
            cache_key = self._generate_cache_key(key, prefix)
            
            result = await client.delete(cache_key)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def exists(self, key: str, prefix: str = "app") -> bool:
        \"\"\"Check if cache key exists\"\"\"
        try:
            client = self._get_client()
            cache_key = self._generate_cache_key(key, prefix)
            
            result = await client.exists(cache_key)
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"Cache exists check failed for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1, prefix: str = "app") -> Optional[int]:
        \"\"\"Increment cache value atomically\"\"\"
        try:
            client = self._get_client()
            cache_key = self._generate_cache_key(key, prefix)
            
            result = await client.incrby(cache_key, amount)
            return int(result)
            
        except Exception as e:
            self.logger.error(f"Cache increment failed for key {key}: {e}")
            return None
    
    async def set_with_lock(
        self, 
        key: str, 
        value: Any, 
        lock_timeout: int = 10,
        ttl: Optional[int] = None,
        prefix: str = "app"
    ) -> bool:
        \"\"\"Set value with distributed lock\"\"\"
        lock_key = f"lock:{key}"
        lock_value = f"{time.time()}:{id(self)}"
        
        try:
            client = self._get_client()
            
            # Acquire lock
            lock_acquired = await client.set(
                self._generate_cache_key(lock_key, prefix),
                lock_value,
                nx=True,
                ex=lock_timeout
            )
            
            if not lock_acquired:
                return False
            
            try:
                # Set the actual value
                return await self.set(key, value, ttl, prefix)
            finally:
                # Release lock
                await client.delete(self._generate_cache_key(lock_key, prefix))
                
        except Exception as e:
            self.logger.error(f"Cache set with lock failed for key {key}: {e}")
            return False

# Cache strategies implementation
class CacheStrategies:
    def __init__(self, cache_client: ProductionCacheClient):
        self.cache = cache_client
        self.logger = logging.getLogger(__name__)
    
    async def cache_aside(
        self, 
        key: str, 
        data_loader: Callable, 
        ttl: Optional[int] = None
    ) -> Any:
        \"\"\"Cache-aside pattern implementation\"\"\"
        # Try to get from cache first
        cached_value = await self.cache.get(key)
        if cached_value is not None:
            return cached_value
        
        # Load from data source
        try:
            value = await data_loader()
            if value is not None:
                # Store in cache
                await self.cache.set(key, value, ttl)
            return value
        except Exception as e:
            self.logger.error(f"Data loader failed for key {key}: {e}")
            raise
    
    async def write_through(
        self,
        key: str,
        value: Any,
        data_writer: Callable,
        ttl: Optional[int] = None
    ) -> bool:
        \"\"\"Write-through pattern implementation\"\"\"
        try:
            # Write to data source first
            await data_writer(value)
            
            # Then update cache
            return await self.cache.set(key, value, ttl)
            
        except Exception as e:
            self.logger.error(f"Write-through failed for key {key}: {e}")
            raise
    
    async def refresh_ahead(
        self,
        key: str,
        data_loader: Callable,
        refresh_threshold: float = 0.8,
        ttl: Optional[int] = None
    ) -> Any:
        \"\"\"Refresh-ahead pattern implementation\"\"\"
        cached_value = await self.cache.get(key)
        
        if cached_value is not None:
            # Check if we need to refresh proactively
            client = self.cache._get_client()
            cache_key = self.cache._generate_cache_key(key)
            remaining_ttl = await client.ttl(cache_key)
            
            if remaining_ttl > 0:
                total_ttl = ttl or self.cache.config.default_ttl
                if remaining_ttl < (total_ttl * (1 - refresh_threshold)):
                    # Refresh in background
                    asyncio.create_task(self._background_refresh(key, data_loader, ttl))
            
            return cached_value
        
        # Cache miss, load synchronously
        value = await data_loader()
        if value is not None:
            await self.cache.set(key, value, ttl)
        return value
    
    async def _background_refresh(self, key: str, data_loader: Callable, ttl: Optional[int]):
        \"\"\"Background refresh task\"\"\"
        try:
            value = await data_loader()
            if value is not None:
                await self.cache.set(key, value, ttl)
                self.logger.debug(f"Background refresh completed for key: {key}")
        except Exception as e:
            self.logger.error(f"Background refresh failed for key {key}: {e}")

# Cache warming implementation
class CacheWarmer:
    def __init__(self, cache_client: ProductionCacheClient):
        self.cache = cache_client
        self.logger = logging.getLogger(__name__)
    
    async def warm_user_data(self, user_ids: List[str], data_loader: Callable) -> int:
        \"\"\"Warm cache with user data\"\"\"
        warmed_count = 0
        
        # Process in batches to avoid overwhelming the data source
        batch_size = 50
        
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i + batch_size]
            
            try:
                # Load batch data
                batch_data = await data_loader(batch)
                
                # Store each item in cache
                for user_id, user_data in batch_data.items():
                    cache_key = f"user:{user_id}"
                    if await self.cache.set(cache_key, user_data):
                        warmed_count += 1
                
                # Small delay between batches
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Cache warming failed for batch starting at index {i}: {e}")
        
        self.logger.info(f"Cache warming completed: {warmed_count} items warmed")
        return warmed_count
    
    async def warm_popular_content(self, content_ids: List[str], data_loader: Callable) -> int:
        \"\"\"Warm cache with popular content\"\"\"
        warmed_count = 0
        
        # Use concurrent processing for independent items
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        async def warm_single_content(content_id: str):
            async with semaphore:
                try:
                    content_data = await data_loader(content_id)
                    if content_data:
                        cache_key = f"content:{content_id}"
                        if await self.cache.set(cache_key, content_data):
                            return 1
                except Exception as e:
                    self.logger.error(f"Failed to warm content {content_id}: {e}")
                return 0
        
        # Process all content concurrently
        tasks = [warm_single_content(content_id) for content_id in content_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        warmed_count = sum(r for r in results if isinstance(r, int))
        self.logger.info(f"Content cache warming completed: {warmed_count} items warmed")
        return warmed_count

# Usage example with FastAPI
from fastapi import FastAPI, Depends

app = FastAPI()

# Initialize cache
cache_config = CacheConfig(
    cluster_nodes=["localhost:7000", "localhost:7001", "localhost:7002"],
    default_ttl=3600,
    max_connections=100
)
cache_client = ProductionCacheClient(cache_config)
cache_strategies = CacheStrategies(cache_client)

@app.on_event("startup")
async def startup_event():
    await cache_client.initialize()

@app.on_event("shutdown") 
async def shutdown_event():
    if cache_client.redis_client:
        await cache_client.redis_client.close()
    if cache_client.cluster_client:
        await cache_client.cluster_client.close()

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    \"\"\"Get user with cache-aside pattern\"\"\"
    
    async def load_user_from_db():
        # Your database query here
        return {"id": user_id, "name": "John Doe", "email": "john@example.com"}
    
    user_data = await cache_strategies.cache_aside(
        key=f"user:{user_id}",
        data_loader=load_user_from_db,
        ttl=1800  # 30 minutes
    )
    
    return user_data

@app.post("/users/{user_id}")
async def update_user(user_id: str, user_data: dict):
    \"\"\"Update user with write-through pattern\"\"\"
    
    async def save_user_to_db(data):
        # Your database update here
        pass
    
    await cache_strategies.write_through(
        key=f"user:{user_id}",
        value=user_data,
        data_writer=lambda data: save_user_to_db(data),
        ttl=1800
    )
    
    return {"message": "User updated successfully"}
```

## 📊 Cache Monitoring and Health Checks

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
cache_hits = Counter('cache_hits_total', 'Total cache hits', ['cache_type'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['cache_type']) 
cache_operations = Histogram('cache_operation_duration_seconds', 'Cache operation duration')

class CacheMonitoring:
    def __init__(self, cache_client: ProductionCacheClient):
        self.cache = cache_client
        self.logger = logging.getLogger(__name__)
    
    async def health_check(self) -> Dict[str, Any]:
        \"\"\"Comprehensive cache health check\"\"\"
        try:
            client = self.cache._get_client()
            
            # Basic ping test
            start_time = time.time()
            await client.ping()
            ping_time = time.time() - start_time
            
            # Get Redis info
            info = await client.info()
            
            # Check memory usage
            memory_usage = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            memory_percent = (memory_usage / max_memory * 100) if max_memory > 0 else 0
            
            # Connection count
            connected_clients = info.get('connected_clients', 0)
            
            return {
                "status": "healthy",
                "ping_time": ping_time,
                "memory_usage_bytes": memory_usage,
                "memory_usage_percent": memory_percent,
                "connected_clients": connected_clients,
                "circuit_breaker_failures": self.cache._circuit_breaker_failures,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "circuit_breaker_failures": self.cache._circuit_breaker_failures,
                "timestamp": time.time()
            }
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        \"\"\"Get detailed cache statistics\"\"\"
        client = self.cache._get_client()
        info = await client.info()
        
        return {
            "keyspace_hits": info.get('keyspace_hits', 0),
            "keyspace_misses": info.get('keyspace_misses', 0),
            "hit_rate": info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)),
            "evicted_keys": info.get('evicted_keys', 0),
            "expired_keys": info.get('expired_keys', 0),
            "used_memory_human": info.get('used_memory_human', '0B'),
            "connected_clients": info.get('connected_clients', 0),
        }

# Health check endpoint
@app.get("/health/cache")
async def cache_health():
    monitor = CacheMonitoring(cache_client)
    return await monitor.health_check()
```

This implementation provides enterprise-grade Redis caching with clustering, circuit breaker patterns, multiple caching strategies, cache warming, and comprehensive monitoring for production applications.""",
            "category": "performance",
            "priority": "high",
            "rationale": "Production-ready caching architecture with Redis clustering, multiple caching patterns, circuit breaker protection, cache warming strategies, and comprehensive monitoring. Essential for high-performance applications.",
            "source": ["https://redis.io/docs/management/scaling/", "https://redis-py.readthedocs.io/en/stable/"],
            "loaded_at": datetime.now(timezone.utc).isoformat(),
            "last_retrieved": None
        }
    ]

def test_vector_search_pipeline():
    """Test the complete vector search pipeline"""
    
    test_queries = [
        "implement user authentication with JWT tokens",
        "optimize database performance and connection pooling", 
        "setup Redis caching for high performance applications"
    ]
    
    return test_queries

async def main():
    """Main function: Add examples, test retrieval"""
    load_dotenv()
    
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE EXAMPLES VECTOR PIPELINE TEST")
    logger.info("=" * 80)
    
    # Check if vector search is available
    if not vector_search_engine.is_available():
        logger.error("❌ Vector search engine not available. Check Supabase configuration.")
        logger.error("Required environment variables:")
        logger.error("- SYMMETRA_SUPABASE_URL")
        logger.error("- SYMMETRA_SUPABASE_KEY")
        return
    
    # Get clients
    client = vector_search_engine._get_supabase_client()
    model = vector_search_engine._get_embedding_model()
    
    if not client or not model:
        logger.error("❌ Failed to initialize Supabase client or embedding model")
        return
    
    logger.info("✅ Vector search engine initialized successfully")
    
    # Step 1: Add comprehensive examples to vector database
    logger.info("\n📥 STEP 1: Adding comprehensive examples to vector database...")
    
    examples = get_comprehensive_examples()
    added_rule_ids = []
    
    for i, example in enumerate(examples, 1):
        try:
            logger.info(f"   Processing example {i}/3: {example['title']}")
            
            # Generate embedding for the guidance content
            guidance_text = f"{example['title']} {example['guidance']}"
            embedding = model.encode(guidance_text).tolist()
            
            logger.info(f"   ├── Generated embedding (size: {len(embedding)})")
            
            # Insert rule into database with metadata
            rule_id = str(uuid.uuid4())
            result = client.table('rules').insert({
                'rule_id': rule_id,
                'title': example['title'],
                'guidance': example['guidance'],
                'category': example['category'],
                'priority': example['priority'],
                'rationale': example['rationale'],
                'embedding': json.dumps(embedding),
                'project_id': None,  # Global rule  
                'created_by': None,  # Use None since this field expects UUID
                'keywords': ['comprehensive', 'detailed', 'implementation', example['category']],
                'source': json.dumps(example.get('source', [])),  # Web links documenting the information
                'loaded_at': example.get('loaded_at'),  # When data was loaded
                'last_retrieved': example.get('last_retrieved')  # When data was last retrieved (None initially)
            }).execute()
            
            if result.data:
                rule_id = result.data[0]['rule_id']
                added_rule_ids.append(rule_id)
                logger.info(f"   ✅ Successfully added rule ID: {rule_id}")
            else:
                logger.error(f"   ❌ Failed to add example: {example['title']}")
                
        except Exception as e:
            logger.error(f"   ❌ Error adding example '{example['title']}': {e}")
    
    logger.info(f"\n📊 Added {len(added_rule_ids)} comprehensive examples to vector database")
    
    # Step 2: Test vector search retrieval
    logger.info("\n🔍 STEP 2: Testing vector search retrieval...")
    
    test_queries = test_vector_search_pipeline()
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n   Query {i}: '{query}'")
        
        try:
            # Search for relevant rules
            relevant_rules = vector_search_engine.search_rules(query, limit=2)
            
            if relevant_rules:
                logger.info(f"   ✅ Found {len(relevant_rules)} relevant rules:")
                for rule in relevant_rules:
                    logger.info(f"      - {rule['title']} (similarity: {rule['similarity']:.3f})")
            else:
                logger.warning(f"   ⚠️ No relevant rules found for query")
                
        except Exception as e:
            logger.error(f"   ❌ Search failed for query: {e}")
    
    # Step 3: Test AI guidance integration
    logger.info("\n🤖 STEP 3: Testing AI guidance integration...")
    
    from symmetra.ai_guidance import guidance_engine
    
    try:
        response = guidance_engine.get_guidance(
            action="implement user authentication system",
            context="Building a Python FastAPI application with JWT tokens and rate limiting"
        )
        
        logger.info("   ✅ AI guidance system integration test:")
        logger.info(f"      - Guidance items: {len(response.guidance)}")
        logger.info(f"      - Rules applied: {response.rules_applied}")
        logger.info(f"      - Complexity score: {response.complexity_score}")
        logger.info(f"      - Patterns suggested: {response.patterns}")
        
        # Show first few lines of guidance
        if response.guidance:
            logger.info("   📋 Sample guidance (first 3 lines):")
            for line in response.guidance[:3]:
                logger.info(f"      {line}")
    
    except Exception as e:
        logger.error(f"   ❌ AI guidance integration test failed: {e}")
    
    # Step 4: Cleanup (optional)
    logger.info("\n🧹 STEP 4: Cleanup options")
    logger.info(f"   Added rule IDs for manual cleanup: {added_rule_ids}")
    logger.info("   To clean up test data, run:")
    for rule_id in added_rule_ids:
        logger.info(f"   DELETE FROM rules WHERE rule_id = '{rule_id}';")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ COMPREHENSIVE EXAMPLES VECTOR PIPELINE TEST COMPLETED")
    logger.info("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())