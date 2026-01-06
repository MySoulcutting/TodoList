"""
主题管理模块
用于管理应用的深色和浅色主题
"""
import flet as ft
import json
from pathlib import Path


class ThemeManager:
    """主题管理类"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.is_dark_mode = True  # 默认深色模式
        self.on_theme_changed_callback = None

        # 主题配置文件路径
        self.config_file = Path("theme_config.json")

        # 加载保存的主题设置
        self._load_theme_preference()

    def _load_theme_preference(self):
        """加载保存的主题偏好"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.is_dark_mode = data.get('is_dark_mode', True)
        except Exception as e:
            print(f"加载主题配置失败: {e}")
            self.is_dark_mode = True

    def _save_theme_preference(self):
        """保存主题偏好"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'is_dark_mode': self.is_dark_mode}, f)
        except Exception as e:
            print(f"保存主题配置失败: {e}")

    def get_current_theme_mode(self):
        """获取当前主题模式"""
        return ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT

    def get_theme_config(self):
        """获取当前主题配置"""
        if self.is_dark_mode:
            return self._get_dark_theme()
        else:
            return self._get_light_theme()

    def _get_dark_theme(self):
        """深色主题配置"""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.INDIGO_400,
                on_primary=ft.Colors.WHITE,
                primary_container=ft.Colors.INDIGO_700,
                secondary=ft.Colors.INDIGO_300,
                surface=ft.Colors.GREY_900,
            ),
            use_material3=True,
        )

    def _get_light_theme(self):
        """浅色主题配置 - 优化配色方案"""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.INDIGO_500,           # 主色调：靛蓝色
                on_primary=ft.Colors.WHITE,              # 主色调上的文字
                primary_container=ft.Colors.INDIGO_50,   # 主色调容器
                secondary=ft.Colors.INDIGO_700,          # 次要色
                surface=ft.Colors.WHITE,                 # 表面颜色
            ),
            use_material3=True,
        )

    def toggle_theme(self):
        """切换主题"""
        self.is_dark_mode = not self.is_dark_mode
        self._save_theme_preference()
        self._apply_theme()

        # 触发回调通知主题已改变
        if self.on_theme_changed_callback:
            self.on_theme_changed_callback(self.is_dark_mode)

    def _apply_theme(self):
        """应用主题到页面"""
        self.page.theme_mode = self.get_current_theme_mode()
        self.page.theme = self.get_theme_config()
        self.page.bgcolor = ft.Colors.GREY_900 if self.is_dark_mode else ft.Colors.GREY_50
        self.page.update()

    def apply_initial_theme(self):
        """应用初始主题"""
        self._apply_theme()

    def set_on_theme_changed(self, callback):
        """设置主题改变回调"""
        self.on_theme_changed_callback = callback

    def is_dark(self):
        """是否为深色模式"""
        return self.is_dark_mode

    # 主题颜色获取方法 - 根据当前主题返回不同颜色
    def get_primary_color(self):
        """获取主色调"""
        return ft.Colors.INDIGO_400 if self.is_dark_mode else ft.Colors.INDIGO_500

    def get_secondary_color(self):
        """获取次要颜色"""
        return ft.Colors.INDIGO_300 if self.is_dark_mode else ft.Colors.INDIGO_700

    def get_background_color(self):
        """获取背景颜色"""
        return ft.Colors.GREY_900 if self.is_dark_mode else "#FAFAFA"

    def get_card_color(self):
        """获取卡片背景颜色"""
        return "#1E1E1E" if self.is_dark_mode else ft.Colors.WHITE

    def get_item_bg_color(self):
        """获取列表项背景颜色"""
        return ft.Colors.GREY_800 if self.is_dark_mode else "#F5F5F5"

    def get_text_color(self):
        """获取主文本颜色"""
        return ft.Colors.WHITE if self.is_dark_mode else "#212121"

    def get_secondary_text_color(self):
        """获取次要文本颜色"""
        return ft.Colors.GREY_400 if self.is_dark_mode else "#757575"

    def get_hint_color(self):
        """获取提示文本颜色"""
        return ft.Colors.GREY_500 if self.is_dark_mode else "#9E9E9E"

    def get_border_color(self):
        """获取边框颜色"""
        return ft.Colors.GREY_700 if self.is_dark_mode else "#E0E0E0"

    def get_divider_color(self):
        """获取分割线颜色"""
        return ft.Colors.GREY_700 if self.is_dark_mode else "#EEEEEE"

    def get_input_bg_color(self):
        """获取输入框背景颜色"""
        return ft.Colors.GREY_800 if self.is_dark_mode else ft.Colors.WHITE

    def get_chip_bg_color(self):
        """获取标签背景颜色"""
        return ft.Colors.with_opacity(0.2, ft.Colors.INDIGO_400) if self.is_dark_mode else "#E8EAF6"

    def get_chip_text_color(self):
        """获取标签文本颜色"""
        return ft.Colors.INDIGO_200 if self.is_dark_mode else "#3F51B5"

    def get_completed_text_color(self):
        """获取已完成任务文本颜色"""
        return ft.Colors.GREY_500 if self.is_dark_mode else "#BDBDBD"

    def get_subtitle_color(self):
        """获取副标题颜色"""
        return ft.Colors.WHITE70 if self.is_dark_mode else "#616161"

    def get_icon_color(self):
        """获取图标颜色"""
        return ft.Colors.GREY_400 if self.is_dark_mode else "#757575"

    def get_shadow_color(self):
        """获取阴影颜色"""
        if self.is_dark_mode:
            return ft.Colors.with_opacity(0.3, ft.Colors.BLACK)
        else:
            return ft.Colors.with_opacity(0.08, ft.Colors.BLACK)
