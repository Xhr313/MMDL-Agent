# 检查点接口占位，预留状态持久化扩展
class CheckpointStore:
    def save(self, state):
        raise NotImplementedError

    def load(self, task_id: str):
        raise NotImplementedError

