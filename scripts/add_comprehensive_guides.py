#!/usr/bin/env python3
"""
Add comprehensive implementation guides to Symmetra vector database

This script adds detailed, web-scrape-quality implementation guides
to the Supabase vector database instead of hardcoding them in the application.
"""

import os
import json
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from symmetra.vector_search import vector_search_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_comprehensive_authentication_guide():
    """Add comprehensive authentication implementation guide to vector DB"""
    
    auth_guides = [
        {
            "title": "Complete Authentication System Implementation Guide",
            "guidance": """# Complete Authentication System Implementation Guide

## 🏗️ Architecture Overview

For a production-ready authentication system, implement a layered architecture:
- **Auth Service Layer**: Handles token generation, validation, refresh  
- **Middleware Layer**: Request interceptor for token validation
- **Database Layer**: User storage with proper indexing and security
- **Rate Limiting Layer**: Prevents brute force and abuse

## 🔧 Database Schema Design

```sql
-- Users table with security considerations
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Never store plain passwords
    salt VARCHAR(255) NOT NULL,          -- Unique salt per user
    email_verified BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Refresh tokens table for secure token management
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL, -- Hash the token
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    device_info JSONB,               -- Track device/browser
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

## 🔒 Password Security Implementation

```python
import bcrypt
import secrets
from typing import Tuple

class PasswordManager:
    \"\"\"Enterprise-grade password security\"\"\"
    
    @staticmethod
    def hash_password(password: str) -> Tuple[str, str]:
        \"\"\"Hash password with unique salt\"\"\"
        salt = secrets.token_hex(32)  # 64-character salt
        # Use bcrypt with cost factor 12-15 for production
        hashed = bcrypt.hashpw(
            (password + salt).encode('utf-8'), 
            bcrypt.gensalt(rounds=12)
        )
        return hashed.decode('utf-8'), salt
    
    @staticmethod
    def verify_password(password: str, hash_str: str, salt: str) -> bool:
        \"\"\"Constant-time password verification\"\"\"
        return bcrypt.checkpw(
            (password + salt).encode('utf-8'),
            hash_str.encode('utf-8')
        )
```""",
            "category": "authentication",
            "priority": "high",
            "rationale": "Authentication is the foundation of application security. This comprehensive guide provides enterprise-grade implementation patterns with proper security considerations, database design, and production-ready code examples."
        },
        
        {
            "title": "JWT Token Management Best Practices",
            "guidance": """# JWT Token Management Implementation

## 🎯 Token Strategy

Implement a dual-token approach for security and usability:
- **Access tokens**: Short-lived (15-30 minutes), contain user claims
- **Refresh tokens**: Long-lived (30 days), used to generate new access tokens

## 🔧 Implementation

```python
import jwt
import datetime
import secrets
from typing import Dict, Optional

class TokenManager:
    def __init__(self, secret_key: str, algorithm: str = 'RS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm  # RS256 preferred for production
    
    def generate_tokens(self, user_id: str) -> Dict[str, str]:
        \"\"\"Generate access + refresh token pair\"\"\"
        now = datetime.datetime.utcnow()
        
        # Short-lived access token (15 minutes)
        access_payload = {
            'user_id': user_id,
            'type': 'access',
            'iat': now,
            'exp': now + datetime.timedelta(minutes=15),
            'jti': secrets.token_urlsafe(32)  # Unique token ID
        }
        
        # Long-lived refresh token (30 days)
        refresh_payload = {
            'user_id': user_id,
            'type': 'refresh', 
            'iat': now,
            'exp': now + datetime.timedelta(days=30),
            'jti': secrets.token_urlsafe(32)
        }
        
        return {
            'access_token': jwt.encode(access_payload, self.secret_key, self.algorithm),
            'refresh_token': jwt.encode(refresh_payload, self.secret_key, self.algorithm)
        }

    def validate_token(self, token: str, token_type: str) -> Optional[Dict]:
        \"\"\"Validate and decode token\"\"\"
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get('type') != token_type:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

## 🛡️ Security Considerations

1. **Algorithm Choice**: Use RS256 (RSA + SHA256) for production
2. **Token Storage**: Store refresh tokens hashed in database
3. **Token Rotation**: Implement token rotation on refresh
4. **Blacklisting**: Implement token blacklisting for logout
5. **Expiry**: Keep access tokens short-lived (15-30 minutes)""",
            "category": "authentication", 
            "priority": "high",
            "rationale": "JWT implementation has many security pitfalls. This guide provides secure token management patterns with proper expiry, rotation, and validation strategies."
        },
        
        {
            "title": "Authentication Rate Limiting Implementation",
            "guidance": """# Rate Limiting for Authentication Endpoints

## 🎯 Multi-Layer Rate Limiting

Implement multiple rate limiting layers to prevent abuse:
- **IP-based limiting**: Prevent brute force from single IP
- **Account-based limiting**: Prevent targeted attacks on specific accounts
- **Global limiting**: Protect against distributed attacks

## 🔧 Redis-Based Rate Limiter

```python
from functools import wraps
import redis
import time

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def rate_limit(self, key: str, limit: int, window: int) -> bool:
        \"\"\"Sliding window rate limiting\"\"\"
        current_time = int(time.time())
        pipeline = self.redis.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, current_time - window)
        # Count current requests
        pipeline.zcard(key)
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        # Set expiry
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_requests = results[1]
        
        return current_requests < limit

def auth_rate_limit(limiter: RateLimiter):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            ip = request.remote_addr
            email = request.json.get('email', '')
            
            # IP-based limiting (5 per minute)
            if not limiter.rate_limit(f'auth:ip:{ip}', 5, 60):
                return {'error': 'Rate limit exceeded'}, 429
                
            # Email-based limiting (3 per minute) 
            if email and not limiter.rate_limit(f'auth:email:{email}', 3, 60):
                return {'error': 'Too many attempts for this account'}, 429
                
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
```

## 📊 Rate Limiting Strategy

- **5 attempts per minute per IP**: Prevents brute force attacks
- **3 attempts per minute per account**: Protects specific accounts
- **Progressive delays**: Increase delay after failed attempts
- **Account lockout**: Lock accounts after 5 failed attempts for 15 minutes""",
            "category": "security",
            "priority": "high", 
            "rationale": "Rate limiting is critical for preventing authentication attacks. This implementation provides multi-layer protection with sliding window algorithms."
        },
        
        {
            "title": "Authentication Middleware Implementation",
            "guidance": """# Authentication Middleware for Request Protection

## 🎯 Middleware Pattern

Implement authentication middleware to protect routes automatically:
- **Token extraction**: Get token from Authorization header
- **Token validation**: Verify signature and expiry
- **User context**: Add user info to request context
- **Error handling**: Standardized auth error responses

## 🔧 Flask Implementation

```python
from functools import wraps
from flask import request, jsonify, g

def require_auth(token_manager: TokenManager):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Missing token'}), 401
            
            token = auth_header.split(' ')[1]
            payload = token_manager.validate_token(token, 'access')
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Store user info in request context
            g.user_id = payload['user_id']
            g.token_jti = payload['jti']
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage example
@app.route('/api/protected')
@require_auth(token_manager)
def protected_endpoint():
    user_id = g.user_id
    return jsonify({'message': f'Hello user {user_id}'})
```

## 🔧 FastAPI Implementation

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = token_manager.validate_token(token, 'access')
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload['user_id']

# Usage example  
@app.get("/api/protected")
async def protected_endpoint(user_id: str = Depends(get_current_user)):
    return {"message": f"Hello user {user_id}"}
```""",
            "category": "authentication",
            "priority": "medium",
            "rationale": "Middleware provides consistent authentication across all protected endpoints. This guide shows framework-specific implementations with proper error handling."
        }
    ]
    
    return auth_guides

def main():
    """Add comprehensive guides to vector database"""
    load_dotenv()
    
    # Check if vector search is available
    if not vector_search_engine.is_available():
        logger.error("Vector search engine not available. Check Supabase configuration.")
        return
    
    logger.info("Adding comprehensive authentication guides to vector database...")
    
    # Get authentication guides
    guides = add_comprehensive_authentication_guide()
    
    # Add each guide to the database
    client = vector_search_engine._get_supabase_client()
    model = vector_search_engine._get_embedding_model()
    
    if not client or not model:
        logger.error("Failed to initialize Supabase client or embedding model")
        return
        
    for guide in guides:
        try:
            # Generate embedding for the guidance content
            guidance_text = f"{guide['title']} {guide['guidance']}"
            embedding = model.encode(guidance_text).tolist()
            
            # Insert rule into database
            result = client.table('rules').insert({
                'title': guide['title'],
                'guidance': guide['guidance'],
                'category': guide['category'],
                'priority': guide['priority'],
                'rationale': guide['rationale'],
                'embedding': json.dumps(embedding),
                'project_id': None,  # Global rule
                'created_by': 'system',
                'tags': ['comprehensive', 'implementation', guide['category']]
            }).execute()
            
            if result.data:
                logger.info(f"✅ Added guide: {guide['title']}")
            else:
                logger.error(f"❌ Failed to add guide: {guide['title']}")
                
        except Exception as e:
            logger.error(f"Error adding guide '{guide['title']}': {e}")
    
    logger.info("Finished adding comprehensive guides to vector database")

if __name__ == "__main__":
    main()