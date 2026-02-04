# 长期记忆，决定了 Agent 记不记得以前发生过的事
# TODO检查点接口占位，预留状态持久化扩展，
# 目前只是个占位符（抽象基类），以后实现具体的存储逻辑（如Redis或MySQL）
class CheckpointStore:
    def save(self, state):
        raise NotImplementedError

    def load(self, task_id: str):
        raise NotImplementedError

