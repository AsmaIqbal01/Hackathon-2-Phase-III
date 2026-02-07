"""Rate limiting utilities for authentication endpoints."""
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List


class LoginRateLimiter:
    """In-memory rate limiter for login attempts.

    Implements a sliding window algorithm to track login attempts per email.
    Thread-safe for concurrent requests.

    Attributes:
        max_attempts: Maximum allowed attempts within window
        window: Time window for rate limiting
        attempts: Dictionary mapping email -> list of attempt timestamps
        lock: Thread lock for concurrent access
    """

    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        """Initialize rate limiter.

        Args:
            max_attempts: Maximum attempts allowed (default: 5)
            window_minutes: Time window in minutes (default: 15)
        """
        self.max_attempts = max_attempts
        self.window = timedelta(minutes=window_minutes)
        self.attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, email: str) -> bool:
        """Check if a login attempt is allowed for the given email.

        Args:
            email: Email address to check

        Returns:
            True if attempt is allowed, False if rate limited
        """
        now = datetime.utcnow()
        cutoff = now - self.window

        with self.lock:
            # Remove old attempts outside the window
            self.attempts[email] = [
                attempt_time for attempt_time in self.attempts[email]
                if attempt_time > cutoff
            ]

            # Check if under limit
            return len(self.attempts[email]) < self.max_attempts

    def record_attempt(self, email: str) -> None:
        """Record a login attempt for the given email.

        Args:
            email: Email address to record
        """
        now = datetime.utcnow()
        with self.lock:
            self.attempts[email].append(now)

    def get_retry_after(self, email: str) -> int:
        """Get seconds until oldest attempt expires (rate limit resets).

        Args:
            email: Email address to check

        Returns:
            Seconds until rate limit resets (0 if no limit)
        """
        with self.lock:
            if not self.attempts[email]:
                return 0

            oldest = min(self.attempts[email])
            retry_at = oldest + self.window
            seconds = int((retry_at - datetime.utcnow()).total_seconds())
            return max(0, seconds)

    def clear_attempts(self, email: str) -> None:
        """Clear all attempts for an email (e.g., on successful login).

        Args:
            email: Email address to clear
        """
        with self.lock:
            if email in self.attempts:
                del self.attempts[email]


# Global rate limiter instance
login_rate_limiter = LoginRateLimiter()
