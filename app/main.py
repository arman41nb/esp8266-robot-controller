import flet as ft
from config import config
from websocket_handler import WebSocketHandler
from udp_handler import UDPHandler
from ui_components import UIComponents

class RobotControllerApp:
    # Bit definitions for movements
    RIGHT_FORWARD = 0
    RIGHT_BACK = 1
    TURN_LEFT = 2
    TURN_RIGHT = 3
    LEFT_FORWARD = 4
    LEFT_BACK = 5

    def __init__(self, page: ft.Page):
        self.page = page
        self.theme = config.get("theme")
        self.ws_handler = WebSocketHandler(config.get("esp_ws_url"))
        self.udp_handler = UDPHandler(config.get("esp_ip") or "192.168.4.1", config.get("udp_port") or 12345)
        self.ui = UIComponents(self.theme)
        self.status_text = ft.Text("Status: Ready", size=14, color=self.theme["purple_dark"])
        self.movement_mask = 0
        self.setup_page()
        self.build_ui()

    def setup_page(self):
        self.page.title = "Sazak"
        self.page.bgcolor = self.theme["white"]
        self.page.horizontal_alignment = "center"
        self.page.vertical_alignment = "center"
        self.page.on_resize = self.on_resize
        self.ws_handler.connect()

    def on_resize(self, e):
        # Handle responsive adjustments if needed
        self.page.update()

    def send_message(self, msg):
        if self.ws_handler.send(msg):
            self.status_text.value = f"Sent: {msg}"
        else:
            self.status_text.value = f"Failed to send: {msg}"
        self.page.update()

    def update_movement(self, movement_bit, active):
        if active:
            self.movement_mask |= (1 << movement_bit)
        else:
            self.movement_mask &= ~(1 << movement_bit)
        self.udp_handler.send(bytes([self.movement_mask]))
        self.status_text.value = f"Mask: {self.movement_mask:06b}"
        self.page.update()

    def build_ui(self):
        # Fields
        self.ssid_field = ft.TextField(
            label="SSID",
            prefix_icon=ft.Icons.WIFI,
            border_radius=14,
            bgcolor=self.theme["white"],
        )
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=14,
            bgcolor=self.theme["purple_light"]
        )

        # Settings Sheet
        self.settings_sheet = ft.BottomSheet(
            ft.Container(
                padding=20,
                width=min(420, self.page.width * 0.9),
                bgcolor=self.theme["white"],
                content=ft.Column(
                    spacing=18,
                    controls=[
                        ft.Text("Wi-Fi Settings", size=22, weight="bold", color=self.theme["purple_dark"]),
                        self.ssid_field,
                        self.password_field,
                        ft.FilledButton(
                            "Send to ESP",
                            icon=ft.Icons.SEND,
                            style=ft.ButtonStyle(
                                bgcolor=self.theme["purple"],
                                shape=ft.RoundedRectangleBorder(radius=12)
                            ),
                            on_click=self.update_wifi_credentials,
                        )
                    ]
                ),
            ),
            show_drag_handle=True,
        )
        self.page.overlay.append(self.settings_sheet)

        # Help Dialog
        self.help_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Help"),
            content=ft.Text(
                "برای کنترل ربات از دکمه‌ها استفاده کنید. برای تنظیمات شبکه وارد بخش Settings شوید.",
                size=14
            ),
            actions=[ft.TextButton("Close", on_click=self.close_help)],
        )

        # Menu
        menu_button = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT,
            icon_color=self.theme["purple_dark"],
            items=[
                ft.PopupMenuItem(text="Settings", icon=ft.Icons.SETTINGS, on_click=self.open_settings),
                ft.PopupMenuItem(text="Help", icon=ft.Icons.HELP_OUTLINE, on_click=self.open_help),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(text="Exit", icon=ft.Icons.LOGOUT, on_click=lambda e: self.page.window_close()),
            ]
        )

        # Layout
        content = self.ui.responsive_column([
            ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Sazak Robot Controller", size=28, weight="bold", color=self.theme["purple_dark"]),
                            ft.Text("ESP8266 Access Point Manager", size=14, color=self.theme["purple_dark"]),
                        ],
                    ),
                    menu_button,
                ],
            ),

            ft.Divider(height=1, color=self.theme["purple_dark"]),

            ft.Text(
                "از دکمه‌ها برای کنترل ربات استفاده کنید.",
                size=14,
                color=self.theme["purple_dark"],
                text_align=ft.TextAlign.CENTER,
            ),

            self.status_text,

            # Control buttons
            self.ui.responsive_row([
                # Left buttons
                ft.Column(
                    spacing=10,
                    controls=[
                        self.ui.ctrl_button("▲", self.LEFT_BACK, self.update_movement),  # left back
                        self.ui.ctrl_button("▼", self.LEFT_FORWARD, self.update_movement),  # left forward
                    ]
                ),
                # Center turn buttons
                ft.Column(
                    spacing=10,
                    controls=[
                        self.ui.ctrl_button("◀", self.TURN_LEFT, self.update_movement),  # turn left
                        self.ui.ctrl_button("▶", self.TURN_RIGHT, self.update_movement),  # turn right
                    ]
                ),
                # Right buttons
                ft.Column(
                    spacing=10,
                    controls=[
                        self.ui.ctrl_button("▲", self.RIGHT_BACK, self.update_movement),  # right back
                        self.ui.ctrl_button("▼", self.RIGHT_FORWARD, self.update_movement),  # right forward
                    ]
                ),
            ], alignment="spaceEvenly"),

            # CMD buttons
            self.ui.responsive_row([
                self.ui.small_button("CMD1", "cmd1", self.send_message),
                self.ui.small_button("CMD2", "cmd2", self.send_message),
                self.ui.small_button("CMD3", "cmd3", self.send_message),
                self.ui.small_button("CMD4", "cmd4", self.send_message),
            ], alignment="center")
        ])

        self.page.add(self.ui.glass_container(content))

    def update_wifi_credentials(self, e):
        if not self.ssid_field.value and not self.password_field.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("حداقل یکی از فیلدها را وارد کنید."), bgcolor="#E84A5F")
            self.page.snack_bar.open = True
            self.page.update()
            return

        if self.ssid_field.value:
            self.send_message(f"SSID:{self.ssid_field.value}")
        if self.password_field.value:
            self.send_message(f"PASS:{self.password_field.value}")

        self.settings_sheet.open = False
        self.page.snack_bar = ft.SnackBar(ft.Text("تنظیمات ارسال شد"), bgcolor=self.theme["purple_dark"])
        self.page.snack_bar.open = True
        self.page.update()

    def open_settings(self, e):
        self.settings_sheet.open = True
        self.page.update()

    def close_help(self, e=None):
        self.help_dialog.open = False
        self.page.update()

    def open_help(self, e):
        self.page.dialog = self.help_dialog
        self.help_dialog.open = True
        self.page.update()

def main(page: ft.Page):
    app = RobotControllerApp(page)

ft.app(target=main, view=ft.WEB_BROWSER)