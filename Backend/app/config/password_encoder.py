import bcrypt


class PasswordEncoder:

    def encode(self, raw_password: str) -> str:
        salt = bcrypt.gensalt(rounds=10, prefix=b"2a")
        return bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")

    def matches(self, raw_password: str, encoded_password: str) -> bool:
        if not raw_password or not encoded_password:
            return False
        try:
            return bcrypt.checkpw(raw_password.encode("utf-8"), encoded_password.encode("utf-8"))
        except ValueError:
            return False
