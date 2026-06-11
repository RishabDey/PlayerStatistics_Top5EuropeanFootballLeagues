from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = (
    "postgresql+psycopg2://postgres:Cristiano.7!@localhost:5432/Football_dashboard"
)

engine = create_engine(DATABASE_URL)

query = """
SELECT DISTINCT
    Player,
    Nation,
    ClubName,
    League,
    PlayerID,
    PlayerURL
FROM player_stats
WHERE Season = '2025-2026'
"""

players_df = pd.read_sql(query, engine)

print(f"{len(players_df)} players found.")