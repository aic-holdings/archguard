"""
Test fixtures for hardcoded secret detection

These are intentionally vulnerable code samples for testing security detection.
"""

# API Keys (fake test keys)
OPENAI_API_KEY = "sk-FAKE-OPENAI-KEY-FOR-TESTING-ONLY"
STRIPE_SECRET_KEY = "sk_test_FAKE_STRIPE_KEY_FOR_TESTING"
GITHUB_TOKEN = "ghp_FAKE_GITHUB_TOKEN_FOR_TESTING_ONLY"

# Database credentials
database_config = {
    "host": "localhost",
    "username": "admin",
    "password": "super_secret_password_123",
    "database": "production_db"
}

# AWS credentials (fake test credentials)
AWS_ACCESS_KEY_ID = "AKIA-FAKE-TEST-EXAMPLE"
AWS_SECRET_ACCESS_KEY = "FAKE-SECRET-KEY-FOR-TESTING-PURPOSES-ONLY"

# Social media tokens (fake test tokens)
SLACK_BOT_TOKEN = "fake-slack-token-for-testing-only"
TWITTER_BEARER_TOKEN = "fake-bearer-token-for-testing-purposes-only"

# JWT Secrets
JWT_SECRET = "my-super-secret-jwt-key-that-should-be-in-env"

# Generic secrets
SECRET_KEY = "django-insecure-secret-key-for-development"
ENCRYPTION_KEY = "b64-encoded-encryption-key-32-chars"

# Private keys (shortened for testing)
PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...
-----END PRIVATE KEY-----"""

# API endpoints with embedded secrets
def call_external_api():
    url = "https://api.example.com/data?api_key=FAKE_API_KEY_FOR_TESTING"
    return requests.get(url)

# Connection strings (fake test URIs)
MONGODB_URI = "mongodb://testuser:fakepassword@localhost:27017/testdb"
REDIS_URL = "redis://testuser:fakepassword@localhost:6379/0"

# Mixed with legitimate environment usage (should not trigger)
LEGITIMATE_CONFIG = {
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY"),  # Good practice
    "database_url": os.getenv("DATABASE_URL"),  # Good practice
}

# Comments with secrets (should have lower confidence)
# Example secret: api_key = "FAKE-TEST-KEY" (in comment)
# TODO: Replace hardcoded password "fakepass" with environment variable