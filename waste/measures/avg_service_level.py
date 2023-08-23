from datetime import datetime

from waste.classes import Database


def avg_service_level(db: Database, after: datetime) -> float:
    """
    This measure computes the service level of serviced containers.
    """
    sql = """-- sql
        SELECT AVG(se.volume <= c.capacity)
        FROM service_events AS se
            INNER JOIN source.containers AS c
                ON se.container = c.name
        WHERE se.time > ?;
    """
    row = db.write.execute(sql, [after]).fetchone()
    return row[0] if row[0] is not None else 1.0
