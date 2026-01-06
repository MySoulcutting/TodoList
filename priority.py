"""
任务优先级定义
"""
from enum import Enum
import flet as ft


class Priority(Enum):
    """任务优先级枚举"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"
    NONE = "无"

    @staticmethod
    def get_color(priority):
        """获取优先级对应的颜色"""
        color_map = {
            Priority.HIGH: ft.Colors.RED_400,
            Priority.MEDIUM: ft.Colors.ORANGE_400,
            Priority.LOW: ft.Colors.BLUE_400,
            Priority.NONE: ft.Colors.GREY_600,
        }
        return color_map.get(priority, ft.Colors.GREY_600)

    @staticmethod
    def get_icon(priority):
        """获取优先级对应的图标"""
        icon_map = {
            Priority.HIGH: ft.Icons.FLAG,
            Priority.MEDIUM: ft.Icons.FLAG_OUTLINED,
            Priority.LOW: ft.Icons.FLAG_OUTLINED,
            Priority.NONE: ft.Icons.FLAG_OUTLINED,
        }
        return icon_map.get(priority, ft.Icons.FLAG_OUTLINED)

    @staticmethod
    def from_string(value):
        """从字符串转换为优先级"""
        for priority in Priority:
            if priority.value == value:
                return priority
        return Priority.NONE

    @staticmethod
    def get_all_values():
        """获取所有优先级值"""
        return [p.value for p in Priority]
