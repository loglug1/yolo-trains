import redis


class TaskManager:
    _pool = None
    DEFAULT_TTL = 10

    def __init__(self, redis_host = 'localhost', redis_port = 6379, redis_db = 0):
        if TaskManager._pool is None:
            TaskManager._pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
        self.r = redis.Redis(connection_pool=TaskManager._pool)

    def close(self):
        self.r.close()

    def start_task(self, task_id, ttl = DEFAULT_TTL) -> bool:
        """Marks a task as running for 10 seconds, task needs to be renewed every frame to keep alive"""
        if self.task_status(task_id):
            return False
        self.r.set(task_id, 0, ex=ttl)
        return True

    def renew_task(self, task_id, ttl = DEFAULT_TTL) -> bool:
        """Resets the expiry timer on a task entry (Expiry is set to clear Redis db in case Flask restarts)"""
        self.r.expire(task_id, ttl)

    def task_status(self, task_id) -> bool:
        """Returns true if task has already started, false otherwise"""
        return bool(self.r.exists(task_id))

    def end_task(self, task_id) -> None:
        """Marks a task as completed"""
        self.r.delete(task_id)
