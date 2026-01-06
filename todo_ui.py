import flet as ft
from priority import Priority
from pathlib import Path


class TodoUI:
    """UI组件构建类"""

    def __init__(self, page, task_manager, category_manager, theme_manager):
        self.page = page
        self.task_manager = task_manager
        self.category_manager = category_manager
        self.theme_manager = theme_manager
        self.task_list_column = None
        self.new_task_field = None
        self.category_tabs = None
        self.search_mode = False  # 是否处于搜索模式
        self.search_query = ""  # 搜索关键词
        self.main_card = None  # 存储主卡片引用

    def build_main_ui(self):
        """构建主界面"""
        # 顶部标题
        title = ft.Text(
            "My Tasks",
            size=36,
            weight=ft.FontWeight.BOLD,
            color=self.theme_manager.get_secondary_color(),
        )

        # 统计信息文本
        self.stats_text = ft.Text(
            "",
            size=12,
            color=self.theme_manager.get_secondary_text_color(),
        )

        # 主题切换按钮
        theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE if self.theme_manager.is_dark() else ft.Icons.LIGHT_MODE,
            icon_color=self.theme_manager.get_secondary_color(),
            tooltip="切换主题",
            on_click=self._on_theme_toggle_clicked,
        )

        # 排序按钮
        sort_button = ft.IconButton(
            icon=ft.Icons.SORT,
            icon_color=self.theme_manager.get_secondary_color(),
            tooltip="排序任务",
            on_click=self._on_sort_clicked,
        )

        # 搜索按钮
        search_button = ft.IconButton(
            icon=ft.Icons.SEARCH,
            icon_color=self.theme_manager.get_secondary_color(),
            tooltip="搜索任务",
            on_click=self._on_search_clicked,
        )

        # 清除已完成按钮
        clear_completed_button = ft.IconButton(
            icon=ft.Icons.CLEAR_ALL,
            icon_color=self.theme_manager.get_icon_color(),
            tooltip="清除已完成",
            on_click=self._on_clear_completed_clicked,
        )

        # 添加分类按钮
        add_category_button = ft.IconButton(
            icon=ft.Icons.CREATE_NEW_FOLDER,
            icon_color=self.theme_manager.get_secondary_color(),
            tooltip="添加分类",
            on_click=self._on_add_category_clicked,
        )

        # 工具栏
        toolbar = ft.Row(
            controls=[
                ft.Column(
                    controls=[title, self.stats_text],
                    spacing=0,
                ),
                ft.Container(expand=True),
                theme_button,
                sort_button,
                search_button,
                add_category_button,
                clear_completed_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # 分类标签页
        self._build_category_tabs()

        # 任务列表容器
        self.task_list_column = ft.Column(
            controls=[],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # 输入框
        self.new_task_field = ft.TextField(
            hint_text="添加新任务...",
            border_radius=30,
            bgcolor=self.theme_manager.get_input_bg_color(),
            border_color=self.theme_manager.get_primary_color(),
            focused_border_color=self.theme_manager.get_secondary_color(),
            text_style=ft.TextStyle(color=self.theme_manager.get_text_color()),
            hint_style=ft.TextStyle(color=self.theme_manager.get_hint_color()),
            filled=True,
            expand=True,
            on_submit=self._on_add_task,
        )

        # 添加按钮（圆形悬浮按钮）
        add_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=self.theme_manager.get_primary_color(),
            on_click=self._on_add_task,
            tooltip="添加任务",
        )

        # 底部输入区域
        input_row = ft.Row(
            controls=[
                self.new_task_field,
                add_button,
            ],
            spacing=12,
        )

        # 主内容卡片
        self.main_card = ft.Container(
            content=ft.Column(
                controls=[
                    # 顶部工具栏
                    ft.Container(
                        content=toolbar,
                        padding=ft.Padding(left=0, right=0, top=10, bottom=10),
                    ),
                    # 分类标签页
                    ft.Container(
                        content=self.category_tabs,
                        padding=ft.Padding(left=0, right=0, top=0, bottom=10),
                    ),
                    # 任务列表区域
                    ft.Container(
                        content=self.task_list_column,
                        expand=True,
                    ),
                    # 底部输入区域
                    ft.Container(
                        content=input_row,
                        padding=ft.Padding(left=0, right=0, top=16, bottom=0),
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            bgcolor=self.theme_manager.get_card_color(),
            border_radius=20,
            padding=24,
            expand=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=self.theme_manager.get_shadow_color(),
            ),
        )

        # 更新统计信息
        self._update_stats()

        return self.main_card

    def _build_category_tabs(self):
        """构建分类标签按钮组"""
        # 创建按钮行容器
        self.category_tabs = ft.Row(
            controls=[],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            wrap=False,
        )

        # 使用统一的构建逻辑
        self._rebuild_category_tabs()

    def _on_category_clicked(self, category):
        """分类按钮点击事件"""
        self.category_manager.set_current_category(category.get_name())

    def _on_theme_toggle_clicked(self, e):
        """主题切换按钮点击处理"""
        self.theme_manager.toggle_theme()

    def _on_sort_clicked(self, e):
        """排序按钮点击处理"""
        # 获取当前排序模式
        current_mode = self.task_manager.get_sort_mode()

        # 排序选项
        sort_options = [
            {"mode": "default", "label": "默认顺序", "icon": ft.Icons.CLEAR_ALL},
            {"mode": "priority_high", "label": "优先级 (高→低)", "icon": ft.Icons.PRIORITY_HIGH},
            {"mode": "priority_low", "label": "优先级 (低→高)", "icon": ft.Icons.LOW_PRIORITY},
            {"mode": "time_new", "label": "创建时间 (新→旧)", "icon": ft.Icons.ACCESS_TIME},
            {"mode": "time_old", "label": "创建时间 (旧→新)", "icon": ft.Icons.HISTORY},
            {"mode": "status", "label": "完成状态 (未完成优先)", "icon": ft.Icons.CHECK_CIRCLE_OUTLINE},
        ]

        # 创建排序选项按钮
        sort_buttons = []
        for option in sort_options:
            is_current = (option["mode"] == current_mode)
            btn = ft.ElevatedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(option["icon"], size=18),
                        ft.Text(option["label"], size=14),
                        ft.Icon(ft.Icons.CHECK, size=18) if is_current else ft.Container(width=18),
                    ],
                    spacing=8,
                ),
                bgcolor=self.theme_manager.get_primary_color() if is_current else self.theme_manager.get_item_bg_color(),
                color=ft.Colors.WHITE if is_current else self.theme_manager.get_text_color(),
                on_click=lambda e, mode=option["mode"]: self._apply_sort(mode),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(16, 12, 16, 12),
                ),
            )
            sort_buttons.append(btn)

        def close_dialog(e=None):
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("排序方式"),
            content=ft.Column(
                controls=sort_buttons,
                spacing=8,
                tight=True,
                width=350,
            ),
            actions=[
                ft.TextButton("关闭", on_click=close_dialog),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _apply_sort(self, mode):
        """应用排序"""
        self.task_manager.set_sort_mode(mode)
        # 关闭对话框
        if self.page.overlay:
            for item in self.page.overlay:
                if isinstance(item, ft.AlertDialog):
                    item.open = False
        self.page.update()

    def rebuild_ui(self):
        """重建UI以应用新主题"""
        # 清空页面
        self.page.clean()

        # 重新构建UI
        new_card = self.build_main_ui()
        self.page.add(new_card)

        # 刷新任务列表（会自动更新所有任务的主题）
        self.refresh_task_list()

    def _on_add_category_clicked(self, e):
        """添加分类按钮点击处理"""
        # 图标库
        icon_library = [
            "📁", "📋", "📝", "📌", "📍", "📎", "📂", "🗂️",
            "💼", "🏢", "🏠", "🏡", "🏫", "🏪", "🏛️", "🏭",
            "📚", "📖", "📕", "📗", "📘", "📙", "✏️", "📓",
            "💻", "⌨️", "🖥️", "📱", "☎️", "📞", "📟", "📠",
            "🎯", "🎨", "🎭", "🎪", "🎬", "🎮", "🎲", "🎰",
            "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱",
            "🍎", "🍕", "🍔", "🍟", "🌭", "🍿", "🥤", "☕",
            "❤️", "💚", "💙", "💜", "🧡", "💛", "🤍", "🖤",
            "⭐", "✨", "💫", "🌟", "🔥", "💧", "🌈", "☀️",
            "🚗", "🚕", "🚙", "🚌", "🚎", "🚐", "🚑", "🚒",
        ]

        # 创建图标选择按钮
        selected_icon = {"value": "📋"}  # 默认图标

        def on_icon_selected(icon):
            selected_icon["value"] = icon
            icon_display.value = f"当前图标: {icon}"
            self.page.update()

        # 创建图标按钮列表
        icon_buttons = []
        for icon in icon_library:
            btn = ft.ElevatedButton(
                content=ft.Text(icon, size=20),
                on_click=lambda e, ic=icon: on_icon_selected(ic),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(4, 4, 4, 4),
                ),
                width=50,
                height=50,
            )
            icon_buttons.append(btn)

        # 自定义图标输入
        custom_icon_field = ft.TextField(
            hint_text="或输入自定义图标（emoji）",
            width=200,
            on_change=lambda e: on_icon_selected(e.control.value) if e.control.value else None,
        )

        # 当前选中图标显示
        icon_display = ft.Text(
            f"当前图标: {selected_icon['value']}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=self.theme_manager.get_secondary_color(),
        )

        # 分类名称输入
        category_name_field = ft.TextField(
            label="分类名称",
            hint_text="输入分类名称...",
            autofocus=True,
            width=250,
        )

        def close_dialog(e=None):
            dialog.open = False
            self.page.update()

        def add_category(e):
            name = category_name_field.value
            if name and name.strip():
                icon = selected_icon["value"]
                result = self.category_manager.add_category(
                    name.strip(),
                    icon
                )
                if result:
                    self._show_snackbar(f"已添加分类：{name}")
                    # 刷新界面
                    self.refresh_task_list()
                else:
                    self._show_snackbar("分类名称已存在")
            close_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text("添加分类"),
            content=ft.Column(
                controls=[
                    category_name_field,
                    ft.Divider(),
                    icon_display,
                    ft.Text("选择图标：", weight=ft.FontWeight.BOLD, size=14),
                    ft.Container(
                        content=ft.Row(
                            controls=icon_buttons,
                            wrap=True,
                            spacing=4,
                            run_spacing=4,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        height=250,
                        width=400,
                    ),
                    custom_icon_field,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("添加", on_click=add_category),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _on_add_task(self, e):
        """添加任务事件处理（私有方法）"""
        task_text = self.new_task_field.value
        current_category = self.category_manager.get_current_category()

        # 如果当前是"全部"分类，默认添加到"默认"
        category_name = current_category.get_name()
        if category_name == "全部":
            category_name = "默认"

        task = self.task_manager.add_task(task_text, Priority.NONE, category_name)

        if task:
            # 传递主题管理器给任务
            task.set_theme_manager(self.theme_manager)
            # 清空输入框
            self.new_task_field.value = ""
            self.page.update()

    def _on_search_clicked(self, e):
        """搜索按钮点击处理"""
        # 创建搜索输入框
        search_field = ft.TextField(
            hint_text="搜索任务...",
            autofocus=True,
            expand=True,
        )

        def close_dialog(e=None):
            dialog.open = False
            self.page.update()

        def perform_search(e):
            query = search_field.value
            if query and query.strip():
                self.search_mode = True
                self.search_query = query.strip()
                self._show_search_results()
            close_dialog()

        def clear_search(e):
            self.search_mode = False
            self.search_query = ""
            self.refresh_task_list()
            close_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text("搜索任务"),
            content=ft.Column(
                controls=[
                    search_field,
                    ft.Text("提示：搜索任务标题和内容", size=12, color=ft.Colors.GREY_500),
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("清除搜索", on_click=clear_search),
                ft.TextButton("搜索", on_click=perform_search),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _show_search_results(self):
        """显示搜索结果"""
        # 清空当前显示
        self.task_list_column.controls.clear()

        # 搜索所有任务
        query = self.search_query.lower()
        matching_tasks = [
            task for task in self.task_manager.get_all_tasks()
            if query in task.get_text().lower()
        ]

        if matching_tasks:
            # 添加搜索结果提示
            search_info = ft.Container(
                content=ft.Text(
                    f"搜索结果: 找到 {len(matching_tasks)} 个任务",
                    size=14,
                    color=self.theme_manager.get_secondary_color(),
                ),
                padding=ft.Padding(left=0, right=0, top=0, bottom=10),
            )
            self.task_list_column.controls.append(search_info)

            # 显示匹配的任务，并确保主题正确
            for task in matching_tasks:
                # 确保任务有最新的主题管理器
                task.set_theme_manager(self.theme_manager)
                self.task_list_column.controls.append(task.get_container())
        else:
            # 没有找到结果
            no_result = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.SEARCH_OFF, size=64, color=self.theme_manager.get_icon_color()),
                        ft.Text("没有找到匹配的任务", size=16, color=self.theme_manager.get_hint_color()),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                expand=True,
            )
            self.task_list_column.controls.append(no_result)

        # 更新界面
        self.page.update()

    def _on_clear_completed_clicked(self, e):
        """清除已完成按钮点击处理"""
        completed_count = len(self.task_manager.get_completed_tasks())

        if completed_count == 0:
            # 显示提示
            self._show_snackbar("没有已完成的任务")
            return

        # 确认对话框
        def close_dialog(clear=False):
            dialog.open = False
            self.page.update()

            if clear:
                self.task_manager.clear_completed()
                self._show_snackbar(f"已清除 {completed_count} 个已完成的任务")

        dialog = ft.AlertDialog(
            title=ft.Text("确认清除"),
            content=ft.Text(f"确定要清除 {completed_count} 个已完成的任务吗？"),
            actions=[
                ft.TextButton("取消", on_click=lambda e: close_dialog(False)),
                ft.TextButton("清除", on_click=lambda e: close_dialog(True)),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _show_snackbar(self, message):
        """显示提示消息"""
        snackbar = ft.SnackBar(
            content=ft.Text(message),
            duration=2000,
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()

    def _update_stats(self):
        """更新统计信息"""
        all_tasks = self.task_manager.get_all_tasks()
        total = len(all_tasks)
        completed = len(self.task_manager.get_completed_tasks())
        pending = len(self.task_manager.get_pending_tasks())

        if total > 0:
            completion_rate = (completed / total) * 100
            self.stats_text.value = f"总计 {total} 个任务 | 已完成 {completed} | 未完成 {pending} | 完成率 {completion_rate:.1f}%"
        else:
            self.stats_text.value = "还没有任务，快来添加吧！"

    def refresh_task_list(self):
        """刷新任务列表显示"""
        # 清空当前显示
        self.task_list_column.controls.clear()

        # 根据当前分类获取任务
        current_category = self.category_manager.get_current_category()
        tasks = self.task_manager.get_tasks_by_category(current_category.get_name())

        # 重新添加任务，并确保每个任务都有最新的主题管理器
        for task in tasks:
            # 始终更新主题管理器（重要：主题切换时需要强制更新）
            task.set_theme_manager(self.theme_manager)
            self.task_list_column.controls.append(task.get_container())

        # 重新构建分类按钮组（更新颜色和任务数量）
        self._rebuild_category_tabs()

        # 更新统计信息
        self._update_stats()

        # 更新界面
        self.page.update()

    def _rebuild_category_tabs(self):
        """重新构建分类标签按钮组"""
        # 清空旧按钮
        self.category_tabs.controls.clear()

        current_category = self.category_manager.get_current_category()
        protected_categories = ["全部", "默认"]

        for category in self.category_manager.get_all_categories():
            task_count = self.task_manager.get_category_task_count(category.get_name())

            # 判断是否为当前选中的分类
            is_selected = (category.get_name() == current_category.get_name())

            # 创建按钮文本
            icon = category.get_icon()
            if task_count > 0:
                btn_text = f"{icon} {category.get_name()} ({task_count})"
            else:
                btn_text = f"{icon} {category.get_name()}"

            # 判断是否可以删除（非保护分类）
            can_delete = category.get_name() not in protected_categories

            # 分类按钮（增大尺寸）
            category_btn = ft.ElevatedButton(
                content=ft.Text(btn_text, size=14),
                on_click=lambda e, cat=category: self._on_category_clicked(cat),
                bgcolor=self.theme_manager.get_primary_color() if is_selected else self.theme_manager.get_item_bg_color(),
                color=ft.Colors.WHITE if is_selected else self.theme_manager.get_secondary_text_color(),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                ),
                height=40,
            )

            # 创建菜单项
            menu_items = [
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.EDIT, size=14, color=ft.Colors.BLUE_400),
                            ft.Text("重命名", size=12),
                        ],
                        spacing=6,
                    ),
                    on_click=lambda e, cat_name=category.get_name(): self._on_rename_category(cat_name),
                )
            ]

            # 只有非保护分类才显示删除选项
            if can_delete:
                menu_items.append(
                    ft.PopupMenuItem(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DELETE_OUTLINE, size=14, color=ft.Colors.RED_400),
                                ft.Text("删除", size=12),
                            ],
                            spacing=6,
                        ),
                        on_click=lambda e, cat_name=category.get_name(): self._on_delete_category(cat_name),
                    )
                )

            # 菜单按钮（调大尺寸）
            menu_button = ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                icon_size=16,
                icon_color=self.theme_manager.get_icon_color(),
                tooltip="分类操作",
                items=menu_items,
                menu_padding=ft.Padding(0, 0, 0, 0),
            )

            # 组合成一行（适当间距）
            btn_container = ft.Container(
                content=ft.Row(
                    controls=[category_btn, menu_button],
                    spacing=4,
                    tight=True,
                ),
                padding=ft.Padding(0, 0, 0, 0),
            )
            self.category_tabs.controls.append(btn_container)

    def _on_rename_category(self, category_name):
        """重命名分类"""
        # 获取当前分类对象
        category = self.category_manager.get_category_by_name(category_name)
        if not category:
            return

        # 图标库
        icon_library = [
            "📁", "📋", "📝", "📌", "📍", "📎", "📂", "🗂️",
            "💼", "🏢", "🏠", "🏡", "🏫", "🏪", "🏛️", "🏭",
            "📚", "📖", "📕", "📗", "📘", "📙", "✏️", "📓",
            "💻", "⌨️", "🖥️", "📱", "☎️", "📞", "📟", "📠",
            "🎯", "🎨", "🎭", "🎪", "🎬", "🎮", "🎲", "🎰",
            "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱",
            "🍎", "🍕", "🍔", "🍟", "🌭", "🍿", "🥤", "☕",
            "❤️", "💚", "💙", "💜", "🧡", "💛", "🤍", "🖤",
            "⭐", "✨", "💫", "🌟", "🔥", "💧", "🌈", "☀️",
            "🚗", "🚕", "🚙", "🚌", "🚎", "🚐", "🚑", "🚒",
        ]

        # 创建图标选择按钮
        selected_icon = {"value": category.get_icon()}  # 当前图标

        def on_icon_selected(icon):
            selected_icon["value"] = icon
            icon_display.value = f"当前图标: {icon}"
            self.page.update()

        # 创建图标按钮列表
        icon_buttons = []
        for icon in icon_library:
            btn = ft.ElevatedButton(
                content=ft.Text(icon, size=20),
                on_click=lambda e, ic=icon: on_icon_selected(ic),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding(4, 4, 4, 4),
                ),
                width=50,
                height=50,
            )
            icon_buttons.append(btn)

        # 自定义图标输入
        custom_icon_field = ft.TextField(
            hint_text="或输入自定义图标（emoji）",
            value=category.get_icon(),
            width=200,
            on_change=lambda e: on_icon_selected(e.control.value) if e.control.value else None,
        )

        # 当前选中图标显示
        icon_display = ft.Text(
            f"当前图标: {selected_icon['value']}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=self.theme_manager.get_secondary_color(),
        )

        # 分类名称输入
        new_name_field = ft.TextField(
            label="分类名称",
            hint_text="输入新的分类名称...",
            value=category_name,
            autofocus=True,
            width=250,
        )

        def close_dialog(e=None):
            dialog.open = False
            self.page.update()

        def rename_category(e):
            new_name = new_name_field.value
            new_icon = selected_icon["value"]

            # 如果名称和图标都没变，直接关闭
            if (new_name == category_name and new_icon == category.get_icon()):
                close_dialog()
                return

            if new_name and new_name.strip():
                result = self.category_manager.rename_category(
                    category_name,
                    new_name.strip(),
                    new_icon if new_icon else None
                )
                if result:
                    # 更新该分类下所有任务的分类名称
                    for task in self.task_manager.get_all_tasks():
                        if task.get_category() == category_name:
                            task.set_category(new_name.strip())

                    self._show_snackbar(f"已更新分类「{category_name}」")
                    # 刷新界面
                    self.refresh_task_list()
                else:
                    self._show_snackbar("分类名称已存在")
            close_dialog()

        dialog = ft.AlertDialog(
            title=ft.Text(f"编辑分类「{category_name}」"),
            content=ft.Column(
                controls=[
                    new_name_field,
                    ft.Divider(),
                    icon_display,
                    ft.Text("选择图标：", weight=ft.FontWeight.BOLD, size=14),
                    ft.Container(
                        content=ft.Row(
                            controls=icon_buttons,
                            wrap=True,
                            spacing=4,
                            run_spacing=4,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        height=250,
                        width=400,
                    ),
                    custom_icon_field,
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton("取消", on_click=close_dialog),
                ft.TextButton("确定", on_click=rename_category),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _on_delete_category(self, category_name):
        """删除分类"""
        # 确认对话框
        def close_dialog(delete=False):
            dialog.open = False
            self.page.update()

            if delete:
                # 先将该分类下的任务移动到默认
                self.task_manager.move_tasks_to_category(category_name, "默认")

                # 删除分类
                result = self.category_manager.remove_category(category_name)
                if result:
                    self._show_snackbar(f"已删除分类：{category_name}")
                    # 刷新界面
                    self.refresh_task_list()
                else:
                    self._show_snackbar("无法删除该分类")

        # 检查该分类下是否有任务
        task_count = self.task_manager.get_category_task_count(category_name)
        if task_count > 0:
            content_text = f"分类「{category_name}」下还有 {task_count} 个任务，确定要删除吗？\n删除后这些任务将被移动到「默认」。"
        else:
            content_text = f"确定要删除分类「{category_name}」吗？"

        dialog = ft.AlertDialog(
            title=ft.Text("确认删除"),
            content=ft.Text(content_text),
            actions=[
                ft.TextButton("取消", on_click=lambda e: close_dialog(False)),
                ft.TextButton("删除", on_click=lambda e: close_dialog(True)),
            ],
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
