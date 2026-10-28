class DatabaseManager:
    def __init__(self, config): self._config = config

    @contextmanager
    def transaction(self):
        conn = self._open()          # wrap failures, hide password
        try:
            yield Session(conn)
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()