import flet as ft
from config import config

class UIComponents:
    def __init__(self, theme):
        self.theme = theme

    def glass_container(self, content):
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor=self.theme["white"],
            border_radius=25,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=18,
                color=self.theme["purple_dark"],
                offset=ft.Offset(0, 4),
            ),
            content=content
        )

    def ctrl_button(self, text, movement_bit, update_callback):
        def on_tap_down(e):
            update_callback(movement_bit, True)

        def on_tap_up(e):
            update_callback(movement_bit, False)

        return ft.Container(
            width=80,
            height=70,
            border_radius=20,
            bgcolor=self.theme["purple"],
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=self.theme["purple_dark"],
                offset=ft.Offset(0, 4)
            ),
            content=ft.GestureDetector(
                on_tap_down=on_tap_down,
                on_tap_up=on_tap_up,
                content=ft.Container(
                    width=80,
                    height=70,
                    alignment=ft.alignment.center,
                    content=ft.Text(text, size=24, color=self.theme["purple_dark"], weight="bold")
                )
            )
        )

    def small_button(self, text, msg, msg_callback):
        return ft.Container(
            width=100,
            height=40,
            border_radius=12,
            bgcolor=self.theme["purple"],
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=self.theme["purple_dark"],
                offset=ft.Offset(0, 2)
            ),
            content=ft.ElevatedButton(
                text=text,
                on_click=lambda e: msg_callback(msg),
                style=ft.ButtonStyle(
                    bgcolor="transparent",
                    elevation=0,
                    shape=ft.RoundedRectangleBorder(radius=12)
                )
            )
        )

    def responsive_row(self, controls, alignment="center"):
        return ft.Row(
            alignment=alignment,
            spacing=10,
            controls=controls,
            wrap=True  # Allow wrapping for small screens
        )

    def responsive_column(self, controls, spacing=10, horizontal_alignment="center"):
        return ft.Column(
            spacing=spacing,
            horizontal_alignment=horizontal_alignment,
            controls=controls,
            scroll=ft.ScrollMode.AUTO if len(controls) > 10 else None
        )