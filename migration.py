import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE users ADD COLUMN phone_number TEXT;")
except sqlite3.OperationalError:
    pass  # Column already exists
try:
    cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT;")
except sqlite3.OperationalError:
    pass
conn.commit()
conn.close()
print("Migration completed!")
