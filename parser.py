import urllib.parse

# 1. Paste your raw password here
password = "1012Sambit7991" 

# 2. Paste the rest of your details
user = "postgres"
host = "db.izvyclsgtnuyauebbuwr.supabase.co"
port = "5432"
dbname = "postgres"

# 3. This generates the safe encoded string
safe_password = urllib.parse.quote_plus(password)
connection_string = f"postgresql://{user}:{safe_password}@{host}:{port}/{dbname}?sslmode=require"

print("\nCopy this into your secrets.toml:")
print(f'DATABASE_URL = "{connection_string}"')