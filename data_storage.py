"""
数据持久化模块
使用 JSON 格式保存和加载任务数据
"""
import json
import os
from datetime import datetime
from priority import Priority


class DataStorage:
    """数据存储管理类"""

    def __init__(self, file_path="todo_data.json"):
        self.file_path = file_path

    def save_data(self, tasks, categories, sort_mode="default"):
        """保存所有数据到文件"""
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "sort_mode": sort_mode,
            "categories": self._serialize_categories(categories),
            "tasks": self._serialize_tasks(tasks),
        }

        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False

    def load_data(self):
        """从文件加载数据"""
        if not os.path.exists(self.file_path):
            return None

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"加载数据失败: {e}")
            return None

    def _serialize_categories(self, categories):
        """序列化分类数据"""
        result = []
        for category in categories:
            result.append({
                "name": category.get_name(),
                "icon": category.get_icon(),
                "color": category.get_color(),
            })
        return result

    def _serialize_tasks(self, tasks):
        """序列化任务数据"""
        result = []
        for task in tasks:
            task_data = {
                "text": task.get_text(),
                "completed": task.is_completed(),
                "priority": task.get_priority().value,
                "category": task.get_category(),
                "created_time": task.get_created_time().isoformat() if task.get_created_time() else None,
                "completed_time": task.get_completed_time().isoformat() if task.get_completed_time() else None,
                "time_format": task.get_time_format(),
                "subtasks": self._serialize_subtasks(task.subtasks),
            }
            result.append(task_data)
        return result

    def _serialize_subtasks(self, subtasks):
        """序列化子任务数据"""
        result = []
        for subtask in subtasks:
            result.append({
                "text": subtask.text,
                "completed": subtask.is_completed(),
            })
        return result

    @staticmethod
    def deserialize_priority(priority_value):
        """反序列化优先级"""
        return Priority.from_string(priority_value)
