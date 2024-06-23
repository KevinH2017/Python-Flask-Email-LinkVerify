# The secret this generates is safe to be used in URLs and is timed to expire
from itsdangerous import URLSafeTimedSerializer
import os

secret = os.urandom(12)

def generate_confirmation_token(email):
    """Generates a secret key to transform email into url safe text"""
    serializer = URLSafeTimedSerializer(secret)
    return serializer.dumps(email)

def confirm_token(token, expiration=3600):
    """Confirms if user token matches token associated with email, expiration measured in seconds.
    3600 = 1 hour"""
    serializer = URLSafeTimedSerializer(secret)
    try:
        email = serializer.loads(
            token,
            max_age=expiration
        )
    except:
        return False
    return email