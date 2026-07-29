"""In-memory credential store for local development.

No persistence layer exists in this repository yet (out of scope for
this pass) — this replaces the previous `/login`, which accepted any
request with no credential check at all. Passwords are never stored in
plaintext; only a bcrypt hash is kept in memory, and it is recomputed
(with a fresh salt) each time the process starts.

Replace with a database-backed user store when persistence work is
scheduled.
"""

import bcrypt

# Seed password for the single development user this store ships with.
# Not a real user base — see README "Local login".
_DEMO_PASSWORD = b"ChangeMe123!"


class InMemoryUserStore:
    """Minimal credential store: username -> bcrypt hash, held in memory.

    Encapsulates user lookup and password verification behind a small
    interface so callers never touch the underlying storage directly.
    """

    def __init__(self) -> None:
        self._users: dict[str, bytes] = {
            "admin": bcrypt.hashpw(_DEMO_PASSWORD, bcrypt.gensalt()),
        }

    def verify_credentials(self, username: str, password: str) -> bool:
        """Return True if `username` exists and `password` matches its hash."""
        hashed = self._users.get(username)
        if hashed is None:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), hashed)


_default_store = InMemoryUserStore()


def verify_credentials(username: str, password: str) -> bool:
    """Module-level convenience wrapper around the default user store."""
    return _default_store.verify_credentials(username, password)
