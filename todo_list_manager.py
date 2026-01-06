from todo_item import TodoItem
from priority import Priority
from datetime import datetime
import flet as ft


class TodoListManager:
    """任务列表管理类"""

    def __init__(self, page):
        self.page = page
        self.tasks = []
        self.on_list_changed_callback = None
        self.category_manager = None  # 用于获取分类列表
        self.sort_mode = "default"  # 排序模式：default, priority_high, priority_low, time_new, time_old

    def set_category_manager(self, category_manager):
        """设置分类管理器"""
        self.category_manager = category_manager

    def add_task(self, task_text, priority=Priority.NONE, category="默认"):
        """添加任务"""
        if not task_text or not task_text.strip():
            return None

        # 创建新任务
        task = TodoItem(task_text.strip(), self.page, priority, category)
        task.set_on_delete(self._on_task_delete)
        task.set_on_status_change(self._on_task_status_change)
        task.set_on_category_change_request(self._on_task_category_change_request)

        # 添加到列表
        self.tasks.append(task)

        # 通知列表变化
        if self.on_list_changed_callback:
            self.on_list_changed_callback()

        return task

    def restore_task(self, task_text, priority, category, completed, subtasks_data, created_time=None, completed_time=None, time_format=None):
        """从数据恢复任务（不触发保存）"""
        task = TodoItem(task_text, self.page, priority, category)
        task.set_on_delete(self._on_task_delete)
        task.set_on_status_change(self._on_task_status_change)
        task.set_on_category_change_request(self._on_task_category_change_request)

        # 恢复时间信息
        if created_time:
            try:
                task.set_created_time(datetime.fromisoformat(created_time))
            except:
                pass

        if completed_time:
            try:
                task.set_completed_time(datetime.fromisoformat(completed_time))
            except:
                pass

        # 恢复时间格式
        if time_format:
            task.set_time_format(time_format)

        # 恢复完成状态
        if completed:
            task.checkbox.value = True
            task.completed = True
            # 使用主题管理器提供的颜色（如果有的话）
            if task.theme_manager:
                task.task_label.color = task.theme_manager.get_completed_text_color()
            else:
                task.task_label.color = ft.Colors.GREY_500
            task.task_label.text_decoration = ft.TextDecoration.LINE_THROUGH

        # 恢复子任务
        for subtask_data in subtasks_data:
            task.add_subtask(subtask_data["text"])
            # 恢复子任务完成状态
            if subtask_data["completed"] and len(task.subtasks) > 0:
                last_subtask = task.subtasks[-1]
                last_subtask.checkbox.value = True
                last_subtask.completed = True
                # 使用主题管理器提供的颜色（如果有的话）
                if last_subtask.theme_manager:
                    last_subtask.label.color = last_subtask.theme_manager.get_completed_text_color()
                else:
                    last_subtask.label.color = ft.Colors.GREY_600
                last_subtask.label.text_decoration = ft.TextDecoration.LINE_THROUGH

        self.tasks.append(task)
        return task

    def remove_task(self, task):
        """删除任务"""
        if task in self.tasks:
            self.tasks.remove(task)

            # 通知列表变化
            if self.on_list_changed_callback:
                self.on_list_changed_callback()

    def get_all_tasks(self):
        """获取所有任务"""
        return self.tasks

    def get_tasks_by_category(self, category_name):
        """根据分类获取任务"""
        if category_name == "全部":
            tasks = self.tasks
        else:
            tasks = [task for task in self.tasks if task.get_category() == category_name]

        # 应用排序
        return self._apply_sort(tasks)

    def get_completed_tasks(self):
        """获取已完成的任务"""
        return [task for task in self.tasks if task.is_completed()]

    def get_pending_tasks(self):
        """获取未完成的任务"""
        return [task for task in self.tasks if not task.is_completed()]

    def clear_completed(self):
        """清除所有已完成的任务"""
        self.tasks = [task for task in self.tasks if not task.is_completed()]

        # 通知列表变化
        if self.on_list_changed_callback:
            self.on_list_changed_callback()

    def get_category_task_count(self, category_name):
        """获取某个分类的任务数量"""
        if category_name == "全部":
            return len(self.tasks)
        return len([task for task in self.tasks if task.get_category() == category_name])

    def move_tasks_to_category(self, from_category, to_category):
        """将任务从一个分类移动到另一个分类"""
        for task in self.tasks:
            if task.get_category() == from_category:
                task.set_category(to_category)

        # 通知列表变化
        if self.on_list_changed_callback:
            self.on_list_changed_callback()

    def set_on_list_changed(self, callback):
        """设置列表变化回调"""
        self.on_list_changed_callback = callback

    def set_sort_mode(self, mode):
        """设置排序模式"""
        self.sort_mode = mode
        # 触发列表更新
        if self.on_list_changed_callback:
            self.on_list_changed_callback()

    def get_sort_mode(self):
        """获取当前排序模式"""
        return self.sort_mode

    def _apply_sort(self, tasks):
        """应用排序到任务列表"""
        if self.sort_mode == "default":
            # 默认不排序，保持原有顺序
            return tasks
        elif self.sort_mode == "priority_high":
            # 优先级从高到低：高 > 中 > 低 > 无
            priority_order = {
                Priority.HIGH: 0,
                Priority.MEDIUM: 1,
                Priority.LOW: 2,
                Priority.NONE: 3
            }
            return sorted(tasks, key=lambda t: priority_order.get(t.get_priority(), 3))
        elif self.sort_mode == "priority_low":
            # 优先级从低到高：无 > 低 > 中 > 高
            priority_order = {
                Priority.NONE: 0,
                Priority.LOW: 1,
                Priority.MEDIUM: 2,
                Priority.HIGH: 3
            }
            return sorted(tasks, key=lambda t: priority_order.get(t.get_priority(), 0))
        elif self.sort_mode == "time_new":
            # 创建时间从新到旧
            return sorted(tasks, key=lambda t: t.get_created_time(), reverse=True)
        elif self.sort_mode == "time_old":
            # 创建时间从旧到新
            return sorted(tasks, key=lambda t: t.get_created_time())
        elif self.sort_mode == "status":
            # 按完成状态：未完成在前，已完成在后
            return sorted(tasks, key=lambda t: t.is_completed())
        else:
            return tasks

    def _on_task_delete(self, task):
        """任务删除回调（私有方法）"""
        self.remove_task(task)

    def _on_task_status_change(self, task):
        """任务状态改变回调（私有方法）"""
        # 触发保存
        if self.on_list_changed_callback:
            self.on_list_changed_callback()

    def _on_task_category_change_request(self, task):
        """任务分类修改请求回调（私有方法）"""
        if not self.category_manager:
            return

        # 获取所有分类（排除"全部"）
        all_categories = [cat for cat in self.category_manager.get_all_categories() if cat.get_name() != "全部"]

        # 创建分类选择对话框
        category_buttons = []
        for category in all_categories:
            is_current = (category.get_name() == task.get_category())
            btn = ft.ElevatedButton(
                content=ft.Text(f"{category.get_icon()} {category.get_name()}", size=14),
                bgcolor=ft.Colors.INDIGO_600 if is_current else ft.Colors.GREY_800,
                color=ft.Colors.WHITE if is_current else ft.Colors.GREY_400,
                on_click=lambda e, cat_name=category.get_name(): change_category(cat_name),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            )
            category_buttons.append(btn)

        def close_dialog(e=None):
            dialog.open = False
            self.page.update()

        def change_category(new_category):
            if new_category != task.get_category():
                task.set_category(new_category)
                # 触发保存
                if self.on_list_changed_callback:
                    self.on_list_changed_callback()
            close_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text(f"修改任务分类"),
            content=ft.Column(
                controls=[
                    ft.Text(f"任务：{task.get_text()}", size=14, color=ft.Colors.GREY_400),
                    ft.Divider(),
                    ft.Text("选择新分类：", weight=ft.FontWeight.BOLD, size=14),
                    ft.Column(
                        controls=category_buttons,
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                tight=True,
                spacing=10,
                width=300,
                height=400,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
