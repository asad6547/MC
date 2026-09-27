from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRoundFlatIconButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.utils import platform
from kivy.core.window import Window

# Import Android-only modules once, at module load time, so they are
# available everywhere in the file (not just inside one method).
#
# IMPORTANT: these only work in an app actually BUILT with buildozer
# (python-for-android). Running this same .py file inside Pydroid3 is
# NOT the same thing — Pydroid3 is its own Android app that runs your
# script inside its own process; it does not provide the
# org.kivy.android.PythonActivity class or necessarily have
# kivy_garden.webview installed. So these imports are wrapped in
# try/except: if they fail (e.g. under Pydroid3), the app falls back
# to opening links in the system browser instead of crashing.
HAS_JNIUS = False
HAS_WEBVIEW_WIDGET = False

if platform == 'android':
    try:
        from android.runnable import run_on_ui_thread
        from jnius import autoclass
        HAS_JNIUS = True
    except Exception:
        HAS_JNIUS = False

if platform in ('android', 'ios'):
    try:
        from kivy_garden.webview import WebView
        HAS_WEBVIEW_WIDGET = True
    except Exception:
        HAS_WEBVIEW_WIDGET = False


class MCBrowserApp(MDApp):
    def build(self):
        self.title = "MC Browser"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        Window.clearcolor = (0.07, 0.08, 0.12, 1)

        # Tab management state
        self.tabs_list = ["https://www.google.com"]
        self.active_tab_index = 0
        self.web_widget = None  # created lazily, on first open_web_url()

        self.root_layout = MDBoxLayout(orientation='vertical')

        # 1. TOP TOOLBAR
        self.top_bar = self.build_top_bar()
        self.root_layout.add_widget(self.top_bar)

        # 2. HOMEPAGE CONTENT (kept in its own method so it can be rebuilt)
        self.scroll = MDScrollView()
        self.scroll.add_widget(self.build_home_content())
        self.root_layout.add_widget(self.scroll)

        return self.root_layout

    # ------------------------------------------------------------------
    # UI BUILDERS
    # ------------------------------------------------------------------
    def build_top_bar(self):
        top_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height="56dp",
            padding=["12dp", "4dp", "12dp", "4dp"],
            spacing="10dp"
        )
        home_btn = MDIconButton(
            icon="home-outline",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            on_release=self.go_to_home
        )

        profile_btn = MDIconButton(
            icon="account-circle",
            theme_icon_color="Custom",
            icon_color=(0.3, 0.8, 0.4, 1)
        )

        # Working tab counter button
        self.tabs_btn = MDIconButton(
            icon="numeric-1-box-outline",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1),
            on_release=self.show_tabs_dialog
        )
        menu_btn = MDIconButton(
            icon="dots-vertical",
            theme_icon_color="Custom",
            icon_color=(1, 1, 1, 1)
        )

        top_bar.add_widget(home_btn)
        top_bar.add_widget(MDBoxLayout())  # spacer
        top_bar.add_widget(profile_btn)
        top_bar.add_widget(self.tabs_btn)
        top_bar.add_widget(menu_btn)
        return top_bar

    def build_home_content(self):
        content = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            padding="16dp",
            spacing="20dp"
        )

        # Big Google-style logo
        # NOTE: "halign" belongs to MDLabel, not to MDBoxLayout - it was
        # mistakenly used on a MDBoxLayout in the original code, which
        # raises a TypeError. Also removed "bold=True", which is not a
        # valid MDLabel keyword in current KivyMD versions.
        logo_label = MDLabel(
            text="Google",
            font_style="H3",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height="60dp"
        )
        content.add_widget(logo_label)

        # Search bar card
        search_card = MDCard(
            radius=[28, 28, 28, 28],
            md_bg_color=(0.15, 0.17, 0.23, 1),
            size_hint_y=None,
            height="56dp",
            padding=["16dp", "0dp", "16dp", "0dp"]
        )
        search_box = MDBoxLayout(orientation='horizontal', spacing="10dp")
        g_icon = MDIconButton(icon="google", theme_icon_color="Custom", icon_color=(0.2, 0.6, 1, 1))

        self.search_input = MDTextField(
            hint_text="Search Google or type URL",
            mode="line",
            active_line=False,
            size_hint_x=0.8,
            on_text_validate=self.on_search
        )
        mic_icon = MDIconButton(icon="microphone", theme_icon_color="Custom", icon_color=(0.8, 0.8, 0.8, 1))

        search_box.add_widget(g_icon)
        search_box.add_widget(self.search_input)
        search_box.add_widget(mic_icon)
        search_card.add_widget(search_box)
        content.add_widget(search_card)

        # Chips row (AI Mode / Incognito)
        chips_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="40dp", spacing="12dp")
        ai_btn = MDRoundFlatIconButton(
            icon="sparkles", text="AI Mode",
            md_bg_color=(0.15, 0.17, 0.23, 1), text_color=(1, 1, 1, 1), size_hint_x=0.5
        )
        incognito_btn = MDRoundFlatIconButton(
            icon="incognito", text="Incognito",
            md_bg_color=(0.15, 0.17, 0.23, 1), text_color=(1, 1, 1, 1), size_hint_x=0.5
        )
        chips_layout.add_widget(ai_btn)
        chips_layout.add_widget(incognito_btn)
        content.add_widget(chips_layout)

        # Shortcuts grid
        shortcuts_card = MDCard(
            radius=[18, 18, 18, 18],
            md_bg_color=(0.12, 0.14, 0.19, 1),
            size_hint_y=None,
            height="100dp",
            padding="10dp"
        )
        grid = MDGridLayout(cols=4, spacing="10dp")

        shortcuts = [
            ("youtube", "YouTube", "https://m.youtube.com"),
            ("facebook", "Facebook", "https://m.facebook.com"),
            ("cricket", "Cricinfo", "https://www.espncricinfo.com"),
            ("store", "OLX", "https://www.olx.com.pk"),
        ]

        for icon_name, name, url in shortcuts:
            # "halign" removed here too - it does not exist on MDBoxLayout.
            item = MDBoxLayout(orientation='vertical')
            btn = MDIconButton(
                icon=icon_name,
                theme_icon_color="Custom",
                icon_color=(1, 1, 1, 1),
                on_release=lambda x, u=url: self.open_web_url(u)
            )
            lbl = MDLabel(
                text=name,
                font_style="Caption",
                halign="center",
                theme_text_color="Custom",
                text_color=(0.7, 0.7, 0.7, 1)
            )
            item.add_widget(btn)
            item.add_widget(lbl)
            grid.add_widget(item)

        shortcuts_card.add_widget(grid)
        content.add_widget(shortcuts_card)

        return content

    # ------------------------------------------------------------------
    # OPENING LINKS — inside the app's own webview
    # ------------------------------------------------------------------
    def open_web_url(self, url):
        self.tabs_list[self.active_tab_index] = url

        if HAS_WEBVIEW_WIDGET:
            if self.web_widget is None:
                self.web_widget = WebView(url=url)
            else:
                self.web_widget.url = url

            # Swap the home screen out and the webview in.
            if self.scroll.parent is not None:
                self.root_layout.remove_widget(self.scroll)
            if self.web_widget.parent is None:
                self.root_layout.add_widget(self.web_widget)
        else:
            # No embedded webview available (e.g. running under Pydroid3,
            # or on desktop while testing) — fall back to the system
            # browser so the app still does something useful instead of
            # crashing or silently doing nothing.
            import webbrowser
            webbrowser.open(url)

    def on_search(self, instance):
        query = self.search_input.text.strip()
        if query:
            if not query.startswith("http://") and not query.startswith("https://"):
                if "." in query:
                    query = "https://" + query
                else:
                    query = f"https://www.google.com/search?q={query}"
            self.open_web_url(query)

    # ------------------------------------------------------------------
    # NAVIGATION / TABS
    # ------------------------------------------------------------------
    def go_to_home(self, instance):
        # FIX: the original code called self.build(), which creates a
        # brand-new root_layout object and throws it away (since its
        # return value was never reassigned to self.root_layout or the
        # app's root widget). That left the screen blank. Instead we
        # just clear and rebuild the scroll content in place.
        if self.web_widget is not None and self.web_widget.parent is not None:
            self.root_layout.remove_widget(self.web_widget)
        if self.scroll.parent is None:
            self.root_layout.add_widget(self.scroll)

        self.scroll.clear_widgets()
        self.scroll.add_widget(self.build_home_content())

    def show_tabs_dialog(self, instance):
        count = len(self.tabs_list)
        dialog = MDDialog(
            title=f"Open Tabs ({count})",
            text="Naya tab add karne ke liye button dabayein.",
            buttons=[
                MDRaisedButton(
                    text="+ New Tab",
                    on_release=lambda x: self.add_new_tab(dialog)
                )
            ]
        )
        dialog.open()

    def add_new_tab(self, dialog):
        dialog.dismiss()
        self.tabs_list.append("https://www.google.com")
        self.active_tab_index = len(self.tabs_list) - 1

        count = len(self.tabs_list)
        if count <= 9:
            self.tabs_btn.icon = f"numeric-{count}-box-outline"
        else:
            self.tabs_btn.icon = "numeric-9-plus-box-outline"

        self.go_to_home(None)


if __name__ == '__main__':
    MCBrowserApp().run()
