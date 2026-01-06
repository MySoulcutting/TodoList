"""
To-Do List 桌面应用
使用 Flet 库实现的 Material Design 3 风格待办事项应用
"""
import flet as ft
from todo_app import TodoApp


def main(page: ft.Page):
    """应用入口函数"""
    TodoApp(page)


if __name__ == "__main__":
    # 启动 Flet 应用
    ft.run(main)
