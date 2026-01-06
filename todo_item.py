import flet as ft
from priority import Priority
from datetime import datetime


class SubTask:
    """子任务类"""

    def __init__(self, text, page, theme_manager=None):
        self.text = text
        self.page = page
        self.theme_manager = theme_manager
        self.completed = False
        self.on_status_change_callback = None
        self._build_ui()

    def _build_ui(self):
        """构建子任务UI"""
        text_color = self.theme_manager.get_subtitle_color() if self.theme_manager else ft.Colors.WHITE70
        primary_color = self.theme_manager.get_secondary_color() if self.theme_manager else ft.Colors.INDIGO_300

        self.checkbox = ft.Checkbox(
            value=False,
            on_change=self._on_checkbox_changed,
            fill_color=primary_color,
        )

        self.label = ft.Text(
            self.text,
            size=14,
            color=text_color,
        )

        self.container = ft.Container(
            content=ft.Row(
                controls=[
                    self.checkbox,
                    ft.Container(content=self.label, expand=True),
                ],
            ),
            padding=ft.Padding(left=40, right=16, top=4, bottom=4),
        )

    def _on_checkbox_changed(self, e):
        """checkbox 状态改变处理"""
        self.completed = self.checkbox.value

        completed_color = self.theme_manager.get_completed_text_color() if self.theme_manager else ft.Colors.GREY_600
        text_color = self.theme_manager.get_subtitle_color() if self.theme_manager else ft.Colors.WHITE70

        if self.completed:
            self.label.color = completed_color
            self.label.text_decoration = ft.TextDecoration.LINE_THROUGH
        else:
            self.label.color = text_color
            self.label.text_decoration = None

        self.page.update()

        if self.on_status_change_callback:
            self.on_status_change_callback(self)

    def set_on_status_change(self, callback):
        """设置状态改变回调"""
        self.on_status_change_callback = callback

    def get_container(self):
        """获取容器组件"""
        return self.container

    def is_completed(self):
        """是否已完成"""
        return self.completed


class TodoItem:
    """单个待办事项类"""

    def __init__(self, task_text, page, priority=Priority.NONE, category="默认"):
        self.task_text = task_text
        self.page = page
        self.completed = False
        self.priority = priority
        self.category = category  # 任务所属分类
        self.subtasks = []
        self.expanded = False  # 子任务是否展开
        self.theme_manager = None  # 主题管理器

        # 时间字段
        self.created_time = datetime.now()  # 添加时间
        self.completed_time = None  # 完成时间

        self.on_delete_callback = None
        self.on_status_change_callback = None

        # 构建UI组件
        self._build_ui()

    def _build_ui(self):
        """构建UI组件（私有方法）"""
        # 获取主题颜色
        text_color = self.theme_manager.get_text_color() if self.theme_manager else ft.Colors.WHITE
        secondary_text_color = self.theme_manager.get_secondary_text_color() if self.theme_manager else ft.Colors.GREY_400
        chip_bg_color = self.theme_manager.get_chip_bg_color() if self.theme_manager else ft.Colors.with_opacity(0.2, ft.Colors.INDIGO_400)
        chip_text_color = self.theme_manager.get_chip_text_color() if self.theme_manager else ft.Colors.INDIGO_200
        item_bg_color = self.theme_manager.get_item_bg_color() if self.theme_manager else ft.Colors.GREY_800
        primary_color = self.theme_manager.get_primary_color() if self.theme_manager else ft.Colors.INDIGO_400
        secondary_color = self.theme_manager.get_secondary_color() if self.theme_manager else ft.Colors.INDIGO_300
        icon_color = self.theme_manager.get_icon_color() if self.theme_manager else ft.Colors.GREY_500

        # 优先级图标
        self.priority_icon = ft.IconButton(
            icon=Priority.get_icon(self.priority),
            icon_color=Priority.get_color(self.priority),
            icon_size=20,
            tooltip=f"优先级: {self.priority.value}",
            on_click=self._on_priority_clicked,
        )

        # 创建任务文本
        self.task_label = ft.Text(
            self.task_text,
            size=16,
            color=text_color,
        )

        # 分类标签（可点击修改）
        self.category_chip = ft.Container(
            content=ft.Text(
                f"📁 {self.category}",
                size=11,
                color=chip_text_color,
            ),
            bgcolor=chip_bg_color,
            padding=ft.Padding(left=8, right=8, top=2, bottom=2),
            border_radius=8,
            on_click=self._on_category_clicked,
            tooltip="点击修改分类",
            ink=True,
        )

        # 时间信息文本（可点击编辑）
        self.time_info = ft.TextButton(
            content=ft.Text(
                self._format_time_info(),
                size=11,
                color=secondary_text_color,
            ),
            on_click=self._on_time_clicked,
            style=ft.ButtonStyle(
                padding=ft.Padding(4, 2, 4, 2),
            ),
            tooltip="点击编辑时间",
        )

        # 创建 checkbox 用于标记完成状态
        self.checkbox = ft.Checkbox(
            value=False,
            on_change=self._on_checkbox_changed,
            fill_color=primary_color
        )

        # 子任务展开/折叠按钮
        self.expand_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_size=20,
            icon_color=icon_color,
            on_click=self._on_expand_clicked,
            visible=False,  # 默认不显示，有子任务时才显示
        )

        # 添加子任务按钮
        self.add_subtask_button = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            icon_color=secondary_color,
            icon_size=18,
            tooltip="添加子任务",
            on_click=self._on_add_subtask_clicked,
        )

        # 删除按钮（红色垃圾桶图标）
        self.delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_400,
            icon_size=18,
            tooltip="删除任务",
            on_click=self._on_delete_clicked,
        )

        # 子任务容器
        self.subtasks_column = ft.Column(
            controls=[],
            spacing=0,
            visible=False,
        )

        # 主任务行
        main_row = ft.Row(
            controls=[
                self.expand_button,
                self.checkbox,
                ft.Column(
                    controls=[
                        self.task_label,
                        ft.Row(
                            controls=[
                                self.category_chip,
                                self.time_info,
                            ],
                            spacing=8,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                self.priority_icon,
                self.add_subtask_button,
                self.delete_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # 将所有元素放在一个容器中
        self.container = ft.Container(
            content=ft.Column(
                controls=[
                    main_row,
                    self.subtasks_column,
                ],
                spacing=0,
            ),
            bgcolor=item_bg_color,
            border_radius=12,
            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
            margin=ft.Margin(left=0, right=0, top=0, bottom=8),
            border=ft.border.all(2, Priority.get_color(self.priority)) if self.priority != Priority.NONE else None,
            animate=ft.Animation(300, "easeOut"),
        )

    def _on_priority_clicked(self, e):
        """优先级点击处理"""
        # 循环切换优先级
        priorities = [Priority.NONE, Priority.LOW, Priority.MEDIUM, Priority.HIGH]
        current_index = priorities.index(self.priority)
        next_index = (current_index + 1) % len(priorities)
        self.priority = priorities[next_index]

        # 更新UI
        self.priority_icon.icon = Priority.get_icon(self.priority)
        self.priority_icon.icon_color = Priority.get_color(self.priority)
        self.priority_icon.tooltip = f"优先级: {self.priority.value}"
        self.container.border = ft.border.all(2, Priority.get_color(self.priority)) if self.priority != Priority.NONE else None

        self.page.update()

    def _on_expand_clicked(self, e):
        """展开/折叠子任务"""
        self.expanded = not self.expanded
        self.subtasks_column.visible = self.expanded
        self.expand_button.icon = ft.Icons.EXPAND_MORE if self.expanded else ft.Icons.CHEVRON_RIGHT
        self.page.update()

    def _on_add_subtask_clicked(self, e):
        """添加子任务按钮点击处理"""
        # 创建输入对话框
        subtask_field = ft.TextField(
            hint_text="输入子任务内容...",
            autofocus=True,
        )

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def add_subtask(e):
            if subtask_field.value and subtask_field.value.strip():
                self.add_subtask(subtask_field.value.strip())
                close_dialog(e)

        dialog = ft.AlertDialog(
            title=ft.Text("添加子任务"),
            content=subtask_field,
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("添加", on_click=add_subtask),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def add_subtask(self, text):
        """添加子任务"""
        subtask = SubTask(text, self.page, self.theme_manager)
        subtask.set_on_status_change(self._on_subtask_status_changed)
        self.subtasks.append(subtask)

        # 更新UI
        self._refresh_subtasks_display()

    def _refresh_subtasks_display(self):
        """刷新子任务显示"""
        self.subtasks_column.controls.clear()
        for subtask in self.subtasks:
            self.subtasks_column.controls.append(subtask.get_container())

        # 显示/隐藏展开按钮
        self.expand_button.visible = len(self.subtasks) > 0

        # 如果有子任务，自动展开
        if len(self.subtasks) > 0:
            self.expanded = True
            self.subtasks_column.visible = True
            self.expand_button.icon = ft.Icons.EXPAND_MORE

        self.page.update()

    def _on_subtask_status_changed(self, subtask):
        """子任务状态改变回调"""
        # 检查是否所有子任务都完成
        if self.subtasks:
            all_completed = all(st.is_completed() for st in self.subtasks)
            if all_completed and not self.completed:
                # 自动完成主任务
                self.checkbox.value = True
                self._on_checkbox_changed(None)

    def _on_checkbox_changed(self, e):
        """checkbox 状态改变处理（私有方法）"""
        self.completed = self.checkbox.value

        completed_color = self.theme_manager.get_completed_text_color() if self.theme_manager else ft.Colors.GREY_500
        text_color = self.theme_manager.get_text_color() if self.theme_manager else ft.Colors.WHITE

        if self.completed:
            # 已完成：记录完成时间，文字变灰并添加删除线
            self.completed_time = datetime.now()
            self.task_label.color = completed_color
            self.task_label.text_decoration = ft.TextDecoration.LINE_THROUGH
        else:
            # 未完成：清除完成时间，恢复正常样式
            self.completed_time = None
            self.task_label.color = text_color
            self.task_label.text_decoration = None

        # 更新时间信息显示
        if hasattr(self, 'time_info'):
            self.time_info.content.value = self._format_time_info()

        self.page.update()

        if self.on_status_change_callback:
            self.on_status_change_callback(self)

    def _on_time_clicked(self, e):
        """时间信息点击处理 - 编辑时间"""
        # 创建时间编辑对话框
        created_date_field = ft.TextField(
            label="创建日期 (YYYY-MM-DD)",
            value=self.created_time.strftime('%Y-%m-%d'),
            width=200,
        )
        created_time_field = ft.TextField(
            label="创建时间 (HH:MM)",
            value=self.created_time.strftime('%H:%M'),
            width=150,
        )

        completed_date_field = ft.TextField(
            label="完成日期 (YYYY-MM-DD)",
            value=self.completed_time.strftime('%Y-%m-%d') if self.completed_time else "",
            width=200,
            disabled=not self.completed,
        )
        completed_time_field = ft.TextField(
            label="完成时间 (HH:MM)",
            value=self.completed_time.strftime('%H:%M') if self.completed_time else "",
            width=150,
            disabled=not self.completed,
        )

        # 时间格式选择
        format_options = [
            "MM-DD HH:MM",
            "YYYY-MM-DD HH:MM",
            "MM/DD HH:MM",
            "HH:MM MM-DD",
            "YYYY年MM月DD日 HH:MM",
        ]

        current_format = getattr(self, 'time_format', "MM-DD HH:MM")
        format_dropdown = ft.Dropdown(
            label="时间显示格式",
            value=current_format,
            options=[ft.dropdown.Option(fmt) for fmt in format_options],
            width=250,
        )

        def close_dialog(e=None):
            dialog.open = False
            self.page.update()

        def save_time(e):
            try:
                # 解析创建时间
                created_datetime_str = f"{created_date_field.value} {created_time_field.value}"
                new_created_time = datetime.strptime(created_datetime_str, '%Y-%m-%d %H:%M')
                self.set_created_time(new_created_time)

                # 解析完成时间
                if self.completed and completed_date_field.value and completed_time_field.value:
                    completed_datetime_str = f"{completed_date_field.value} {completed_time_field.value}"
                    new_completed_time = datetime.strptime(completed_datetime_str, '%Y-%m-%d %H:%M')
                    self.set_completed_time(new_completed_time)

                # 保存时间格式
                self.time_format = format_dropdown.value

                # 更新显示
                self.time_info.content.value = self._format_time_info()
                self.page.update()

                # 触发保存
                if self.on_status_change_callback:
                    self.on_status_change_callback(self)

                close_dialog()
            except ValueError as ex:
                # 显示错误提示
                error_text.value = f"时间格式错误: {str(ex)}"
                self.page.update()

        error_text = ft.Text("", color=ft.Colors.RED_400, size=12)

        dialog = ft.AlertDialog(
            title=ft.Text("编辑时间"),
            content=ft.Column(
                controls=[
                    ft.Text("创建时间", weight=ft.FontWeight.BOLD, size=14),
                    ft.Row(
                        controls=[created_date_field, created_time_field],
                        spacing=10,
                    ),
                    ft.Divider(),
                    ft.Text("完成时间", weight=ft.FontWeight.BOLD, size=14),
                    ft.Row(
                        controls=[completed_date_field, completed_time_field],
                        spacing=10,
                    ),
                    ft.Divider(),
                    format_dropdown,
                    error_text,
                ],
                tight=True,
                spacing=10,
                width=400,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("保存", on_click=save_time),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _on_category_clicked(self, e):
        """分类标签点击处理 - 修改分类"""
        # 需要从外部获取所有分类列表
        # 通过回调函数获取
        if hasattr(self, 'on_category_change_request'):
            self.on_category_change_request(self)

    def _on_delete_clicked(self, e):
        """删除按钮点击处理（私有方法）"""
        if self.on_delete_callback:
            self.on_delete_callback(self)

    def set_on_delete(self, callback):
        """设置删除回调"""
        self.on_delete_callback = callback

    def set_on_status_change(self, callback):
        """设置状态改变回调"""
        self.on_status_change_callback = callback

    def get_container(self):
        """获取容器组件"""
        return self.container

    def is_completed(self):
        """是否已完成"""
        return self.completed

    def get_text(self):
        """获取任务文本"""
        return self.task_text

    def get_priority(self):
        """获取优先级"""
        return self.priority

    def get_category(self):
        """获取分类"""
        return self.category

    def set_category(self, category):
        """设置分类"""
        self.category = category
        # 更新UI显示
        if hasattr(self, 'category_chip'):
            self.category_chip.content.value = f"📁 {category}"
            self.page.update()

    def set_on_category_change_request(self, callback):
        """设置分类修改请求回调"""
        self.on_category_change_request = callback

    def get_subtasks_count(self):
        """获取子任务数量"""
        return len(self.subtasks)

    def get_completed_subtasks_count(self):
        """获取已完成的子任务数量"""
        return sum(1 for st in self.subtasks if st.is_completed())

    def _format_time_info(self):
        """格式化时间信息显示"""
        time_format = getattr(self, 'time_format', "MM-DD HH:MM")

        # 根据格式选项格式化时间
        if time_format == "MM-DD HH:MM":
            created_str = f"创建: {self.created_time.strftime('%m-%d %H:%M')}"
            completed_str = f"完成: {self.completed_time.strftime('%m-%d %H:%M')}" if self.completed_time else None
        elif time_format == "YYYY-MM-DD HH:MM":
            created_str = f"创建: {self.created_time.strftime('%Y-%m-%d %H:%M')}"
            completed_str = f"完成: {self.completed_time.strftime('%Y-%m-%d %H:%M')}" if self.completed_time else None
        elif time_format == "MM/DD HH:MM":
            created_str = f"创建: {self.created_time.strftime('%m/%d %H:%M')}"
            completed_str = f"完成: {self.completed_time.strftime('%m/%d %H:%M')}" if self.completed_time else None
        elif time_format == "HH:MM MM-DD":
            created_str = f"创建: {self.created_time.strftime('%H:%M %m-%d')}"
            completed_str = f"完成: {self.completed_time.strftime('%H:%M %m-%d')}" if self.completed_time else None
        elif time_format == "YYYY年MM月DD日 HH:MM":
            created_str = f"创建: {self.created_time.strftime('%Y年%m月%d日 %H:%M')}"
            completed_str = f"完成: {self.completed_time.strftime('%Y年%m月%d日 %H:%M')}" if self.completed_time else None
        else:
            # 默认格式
            created_str = f"创建: {self.created_time.strftime('%m-%d %H:%M')}"
            completed_str = f"完成: {self.completed_time.strftime('%m-%d %H:%M')}" if self.completed_time else None

        if completed_str:
            return f"{created_str} | {completed_str}"
        return created_str

    def get_created_time(self):
        """获取创建时间"""
        return self.created_time

    def get_completed_time(self):
        """获取完成时间"""
        return self.completed_time

    def set_created_time(self, time):
        """设置创建时间"""
        self.created_time = time
        if hasattr(self, 'time_info'):
            self.time_info.content.value = self._format_time_info()

    def set_completed_time(self, time):
        """设置完成时间"""
        self.completed_time = time
        if hasattr(self, 'time_info'):
            self.time_info.content.value = self._format_time_info()

    def get_time_format(self):
        """获取时间格式"""
        return getattr(self, 'time_format', "MM-DD HH:MM")

    def set_time_format(self, format_str):
        """设置时间格式"""
        self.time_format = format_str
        if hasattr(self, 'time_info'):
            self.time_info.content.value = self._format_time_info()

    def set_theme_manager(self, theme_manager):
        """设置主题管理器"""
        self.theme_manager = theme_manager
        # 如果已经构建了UI，需要更新颜色
        if hasattr(self, 'task_label'):
            self._update_theme_colors()

    def _update_theme_colors(self):
        """更新主题颜色"""
        if not self.theme_manager:
            return

        # 更新任务文本颜色
        if self.completed:
            self.task_label.color = self.theme_manager.get_completed_text_color()
        else:
            self.task_label.color = self.theme_manager.get_text_color()

        # 更新分类标签颜色
        self.category_chip.bgcolor = self.theme_manager.get_chip_bg_color()
        self.category_chip.content.color = self.theme_manager.get_chip_text_color()

        # 更新时间信息颜色
        self.time_info.content.color = self.theme_manager.get_secondary_text_color()

        # 更新容器背景色
        self.container.bgcolor = self.theme_manager.get_item_bg_color()

        # 更新checkbox颜色
        self.checkbox.fill_color = self.theme_manager.get_primary_color()

        # 更新按钮颜色
        self.expand_button.icon_color = self.theme_manager.get_icon_color()
        self.add_subtask_button.icon_color = self.theme_manager.get_secondary_color()

        # 更新子任务颜色
        for subtask in self.subtasks:
            subtask.theme_manager = self.theme_manager
            if subtask.completed:
                subtask.label.color = self.theme_manager.get_completed_text_color()
            else:
                subtask.label.color = self.theme_manager.get_subtitle_color()
            subtask.checkbox.fill_color = self.theme_manager.get_secondary_color()
