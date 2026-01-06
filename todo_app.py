import flet as ft
from todo_list_manager import TodoListManager
from todo_ui import TodoUI
from category_manager import CategoryManager
from data_storage import DataStorage
from theme_manager import ThemeManager


class TodoApp:
    """待办事项应用主类"""

    def __init__(self, page: ft.Page):
        self.page = page

        # 初始化数据存储
        self.storage = DataStorage()

        # 初始化主题管理器
        self.theme_manager = ThemeManager(page)

        # 初始化各个组件
        self.task_manager = TodoListManager(page)
        self.category_manager = CategoryManager()

        # 设置任务管理器的分类管理器引用
        self.task_manager.set_category_manager(self.category_manager)

        self.ui_builder = TodoUI(page, self.task_manager, self.category_manager, self.theme_manager)

        # 配置页面
        self._setup_page()

        # 加载保存的数据
        self._load_data()

        # 设置回调
        self.task_manager.set_on_list_changed(self._on_task_list_changed)
        self.category_manager.set_on_category_changed(self._on_category_changed)
        self.theme_manager.set_on_theme_changed(self._on_theme_changed)

        # 构建并显示UI
        self._build_and_show_ui()

    def _setup_page(self):
        """配置页面属性（私有方法）"""
        self.page.title = "To-do List"

        # 应用主题
        self.theme_manager.apply_initial_theme()

        # 窗口设置
        self.page.window.width = 800
        self.page.window.height = 900
        self.page.window.resizable = True
        self.page.padding = 20

        # 设置窗口关闭事件
        self.page.on_close = self._on_window_close

    def _load_data(self):
        """加载保存的数据"""
        data = self.storage.load_data()

        if data is None:
            # 没有保存的数据，使用默认设置
            return

        try:
            # 清空现有数据
            self.category_manager.clear_categories()

            # 恢复分类
            if "categories" in data:
                for cat_data in data["categories"]:
                    self.category_manager.restore_category(
                        cat_data["name"],
                        cat_data["icon"],
                        cat_data.get("color")
                    )

                # 设置当前分类为全部
                if self.category_manager.get_all_categories():
                    all_cat = self.category_manager.get_category_by_name("全部")
                    if all_cat:
                        self.category_manager.current_category = all_cat
                    else:
                        self.category_manager.current_category = self.category_manager.get_all_categories()[0]

            # 恢复任务
            if "tasks" in data:
                for task_data in data["tasks"]:
                    priority = DataStorage.deserialize_priority(task_data.get("priority", "无"))
                    task = self.task_manager.restore_task(
                        task_data["text"],
                        priority,
                        task_data.get("category", "默认"),
                        task_data.get("completed", False),
                        task_data.get("subtasks", []),
                        task_data.get("created_time"),
                        task_data.get("completed_time"),
                        task_data.get("time_format")
                    )
                    # 为恢复的任务设置主题管理器
                    if task:
                        task.set_theme_manager(self.theme_manager)

            # 恢复排序模式
            if "sort_mode" in data:
                self.task_manager.sort_mode = data["sort_mode"]

        except Exception as e:
            print(f"加载数据时出错: {e}")
            # 出错时重新初始化默认分类
            self.category_manager.clear_categories()
            self.category_manager._init_default_categories()

    def _save_data(self):
        """保存数据到文件"""
        categories = self.category_manager.get_all_categories()
        tasks = self.task_manager.get_all_tasks()
        sort_mode = self.task_manager.get_sort_mode()
        self.storage.save_data(tasks, categories, sort_mode)

    def _on_window_close(self, e):
        """窗口关闭时保存数据"""
        self._save_data()

    def _build_and_show_ui(self):
        """构建并显示UI（私有方法）"""
        main_card = self.ui_builder.build_main_ui()
        self.page.add(main_card)

        # 初始化时刷新任务列表，显示所有任务
        self.ui_builder.refresh_task_list()

    def _on_task_list_changed(self):
        """任务列表变化回调（私有方法）"""
        self.ui_builder.refresh_task_list()
        # 自动保存数据
        self._save_data()

    def _on_category_changed(self, category):
        """分类改变回调（私有方法）"""
        self.ui_builder.refresh_task_list()
        # 自动保存数据
        self._save_data()

    def _on_theme_changed(self, is_dark):
        """主题改变回调（私有方法）"""
        # 刷新整个UI以应用新主题
        self.ui_builder.rebuild_ui()
