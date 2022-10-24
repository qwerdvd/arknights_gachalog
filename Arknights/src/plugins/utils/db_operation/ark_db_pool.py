import sqlite3

import sqlalchemy.pool as pool  # type: ignore

ark_pool = pool.QueuePool(
    lambda: sqlite3.connect('ID_DATA.db'),
    max_overflow=10,
    pool_size=5,
)
