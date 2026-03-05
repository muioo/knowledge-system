from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt 限制密码最长 72 字节
MAX_PASSWORD_LENGTH = 72


def hash_password(password: str) -> str:
    # bcrypt 限制密码最长 72 字节，截断过长的密码
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > MAX_PASSWORD_LENGTH:
        password = password_bytes[:MAX_PASSWORD_LENGTH].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 验证时也需要截断，以匹配哈希时的处理
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > MAX_PASSWORD_LENGTH:
        plain_password = password_bytes[:MAX_PASSWORD_LENGTH].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)
