from database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        conn.execute(text('GRANT ALL PRIVILEGES ON DATABASE postgres TO "694869740345-compute@developer";'))
        conn.execute(text('GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "694869740345-compute@developer";'))
        conn.commit()
    print("Permissions granted to short username.")
except Exception as e:
    print("Error:", e)
