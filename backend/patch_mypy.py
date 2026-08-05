import re


def replace_in_file(path, pattern, repl):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = re.sub(pattern, repl, content, flags=re.MULTILINE|re.DOTALL)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

replace_in_file('app/repositories/base.py', r'self\.model\.id', r'getattr(self.model, "id")')
replace_in_file('app/repositories/base.py', r'result\.rowcount', r'getattr(result, "rowcount", 0)')

replace_in_file('app/core/config.py', r'    SECRET_KEY: str\n.*DATABASE_URL: str\n    REDIS_URL: str', '    SECRET_KEY: str = ""\n    DATABASE_URL: str = ""\n    REDIS_URL: str = ""')

replace_in_file('app/core/database.py', r'    _engine = None\n    _sessionmaker = None', '    _engine: AsyncEngine | None = None\n    _sessionmaker: async_sessionmaker[AsyncSession] | None = None')

replace_in_file('app/api/dependencies.py', r'token_data: TokenData = TokenData\(sub=user_id\)', 'token_data: TokenData = TokenData(sub=str(user_id) if user_id else None)')
replace_in_file('app/api/dependencies.py', r'token_data\.sub', 'str(token_data.sub)')

replace_in_file('app/core/security.py', r'expires_delta: timedelta = None', r'expires_delta: timedelta | None = None')

replace_in_file('app/services/user_service.py', r'int\(user_id\)', r'int(user_id) if user_id is not None else 0')
replace_in_file('app/services/user_service.py', r'-> User:', r'-> User | None:')

print("Patching complete.")
