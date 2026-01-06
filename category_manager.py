"""
分类/分组管理模块
"""


class Category:
    """分类类"""

    def __init__(self, name, icon=None, color=None):
        self.name = name
        self.icon = icon or "📋"
        self.color = color or "#5C6BC0"  # 默认靛蓝色

    def get_name(self):
        """获取分类名称"""
        return self.name

    def get_icon(self):
        """获取分类图标"""
        return self.icon

    def get_color(self):
        """获取分类颜色"""
        return self.color


class CategoryManager:
    """分类管理器"""

    def __init__(self):
        self.categories = []
        self.current_category = None
        self.on_category_changed_callback = None

        # 初始化默认分类
        self._init_default_categories()

    def _init_default_categories(self):
        """初始化默认分类"""
        default_categories = [
            Category("全部", "📁", "#9E9E9E"),
            Category("默认", "📥", "#5C6BC0"),
            Category("工作", "💼", "#F57C00"),
            Category("生活", "🏠", "#43A047"),
            Category("学习", "📚", "#E53935"),
        ]

        for category in default_categories:
            self.categories.append(category)

        # 默认选中"全部"
        self.current_category = self.categories[0]

    def add_category(self, name, icon=None, color=None):
        """添加新分类"""
        # 检查是否已存在同名分类
        for category in self.categories:
            if category.get_name() == name:
                return None

        new_category = Category(name, icon, color)
        self.categories.append(new_category)
        return new_category

    def restore_category(self, name, icon, color):
        """从数据恢复分类（用于加载保存的数据）"""
        # 检查是否已存在
        for category in self.categories:
            if category.get_name() == name:
                return None

        new_category = Category(name, icon, color)
        self.categories.append(new_category)
        return new_category

    def clear_categories(self):
        """清空所有分类（用于重新加载数据）"""
        self.categories.clear()
        self.current_category = None

    def remove_category(self, category_name):
        """删除分类（不能删除默认分类）"""
        # 保护默认分类
        protected_names = ["全部", "默认"]
        if category_name in protected_names:
            return False

        for category in self.categories:
            if category.get_name() == category_name:
                self.categories.remove(category)
                # 如果删除的是当前分类，切换到默认
                if self.current_category == category:
                    self.set_current_category("默认")
                return True

        return False

    def get_all_categories(self):
        """获取所有分类"""
        return self.categories

    def get_current_category(self):
        """获取当前选中的分类"""
        return self.current_category

    def set_current_category(self, category_name):
        """设置当前分类"""
        for category in self.categories:
            if category.get_name() == category_name:
                self.current_category = category
                # 通知分类改变
                if self.on_category_changed_callback:
                    self.on_category_changed_callback(category)
                return True
        return False

    def set_on_category_changed(self, callback):
        """设置分类改变回调"""
        self.on_category_changed_callback = callback

    def get_category_by_name(self, name):
        """根据名称获取分类"""
        for category in self.categories:
            if category.get_name() == name:
                return category
        return None

    def rename_category(self, old_name, new_name, new_icon=None):
        """重命名分类（支持修改名称和图标）"""
        # 检查新名称是否已存在（如果名称改变了）
        if new_name != old_name and self.get_category_by_name(new_name):
            return False

        category = self.get_category_by_name(old_name)
        if category:
            category.name = new_name
            if new_icon:
                category.icon = new_icon
            # 通知分类改变
            if self.on_category_changed_callback:
                self.on_category_changed_callback(category)
            return True
        return False
