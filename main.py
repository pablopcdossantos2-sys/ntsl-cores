"""
NTSL Cores — editor visual de cores para indicadores NTSL.
Dependências: customtkinter e Pillow. Python 3.9+
"""
import json
import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, messagebox

import customtkinter as ctk
from PIL import Image, ImageDraw


NATIVE_COLORS = [
    ("clAqua", "Azul-claro", "#00ffff"),
    ("clBlack", "Preto", "#000000"),
    ("clAzul", "Azul", "#0000ff"),
    ("clCreme", "Creme", "#fffdd0"),
    ("clCinzaEscuro", "Cinza-escuro", "#555555"),
    ("clFucsia", "Fúcsia", "#ff00ff"),
    ("clCinza", "Cinza", "#808080"),
    ("clVerde", "Verde", "#008000"),
    ("clVerdeLimao", "Verde-limão", "#32cd32"),
    ("clCinzaClaro", "Cinza-claro", "#d3d3d3"),
    ("clMarrom", "Marrom", "#a52a2a"),
    ("clCinzaMedio", "Cinza médio", "#a0a0a0"),
    ("clVerdeClaro", "Verde-claro", "#90ee90"),
    ("clAzulMarinho", "Azul-marinho", "#000080"),
    ("clVerdeOliva", "Verde-oliva", "#808000"),
    ("clPurpura", "Púrpura", "#800080"),
    ("clVermelho", "Vermelho", "#ff0000"),
    ("clPrata", "Prata", "#c0c0c0"),
    ("clAzulClaro", "Azul-claro", "#87ceeb"),
    ("clTeal", "Verde-azulado", "#008080"),
    ("clBranco", "Branco", "#ffffff"),
    ("clAmarelo", "Amarelo", "#ffff00"),
]
EXAMPLE_COLORS = [
    ("clRed", "Vermelho (exemplo)", "#ff0000"),
    ("clGreen", "Verde (exemplo)", "#008000"),
    ("clWhite", "Branco (exemplo)", "#ffffff"),
    ("clYellow", "Amarelo (exemplo)", "#ffff00"),
]

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def favorites_file():
    base = os.environ.get("APPDATA")
    folder = Path(base) / "NTSLCores" if base else Path.home() / ".ntsl-cores"
    return folder / "favorites.json"


class NTSLCoresApp(ctk.CTk):
    BG = "#111318"
    SIDEBAR = "#171a21"
    PANEL = "#1b1f28"
    PANEL_ALT = "#222733"
    BORDER = "#2b3240"
    TEXT = "#f3f5f9"
    MUTED = "#929bad"
    BLUE = "#5b8cff"
    GREEN = "#31b987"

    def __init__(self):
        super().__init__()
        self.title("NTSL Cores")
        self.geometry("1160x820")
        self.minsize(980, 720)
        self.configure(fg_color=self.BG)

        self.variable_name = tk.StringVar(value="cor")
        self.rgb = {"r": 115, "g": 65, "b": 30}
        self.rgb_vars = {k: tk.IntVar(value=v) for k, v in self.rgb.items()}
        self.rgb_entries = {}
        self.rgb_sliders = {}
        self.selected_native = NATIVE_COLORS[16]
        self.mode = "rgb"
        self._syncing = False
        self.selected_favorite = None
        self.search_var = tk.StringVar()
        self.favorites_path = favorites_file()
        self.favorites = self._load_favorites()
        self.nav_buttons = {}
        self.pages = {}

        self._build_shell()
        self._build_rgb_page()
        self._build_native_page()
        self._build_favorites_page()
        self.show_page("rgb")
        self._refresh_rgb()
        self._render_native_cards()
        self._render_favorites()

    def _load_favorites(self):
        try:
            with self.favorites_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            result = []
            for item in data if isinstance(data, list) else []:
                try:
                    name = str(item["name"]).strip()
                    r, g, b = (int(item[k]) for k in ("r", "g", "b"))
                    if name and all(0 <= v <= 255 for v in (r, g, b)):
                        result.append({"name": name, "r": r, "g": g, "b": b})
                except (KeyError, TypeError, ValueError):
                    pass
            return result
        except (OSError, json.JSONDecodeError):
            return []

    def _save_favorites(self):
        try:
            self.favorites_path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.favorites_path.with_suffix(".tmp")
            with temp.open("w", encoding="utf-8") as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
            temp.replace(self.favorites_path)
            return True
        except OSError as exc:
            messagebox.showerror("Erro ao salvar", f"Não foi possível salvar a paleta.\n\n{exc}", parent=self)
            return False

    @staticmethod
    def _hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    def _card(self, parent, **kwargs):
        return ctk.CTkFrame(parent, fg_color=self.PANEL, corner_radius=16,
                            border_width=1, border_color=self.BORDER, **kwargs)

    def _label(self, parent, text, size=12, color=None, weight="normal", **kwargs):
        return ctk.CTkLabel(parent, text=text, font=("Segoe UI", size, weight),
                            text_color=color or self.TEXT, **kwargs)

    def _button(self, parent, text, command, kind="primary", **kwargs):
        styles = {
            "primary": (self.BLUE, "#4777df", "#ffffff"),
            "success": (self.GREEN, "#249a70", "#ffffff"),
            "secondary": (self.PANEL_ALT, "#30394a", self.TEXT),
            "danger": ("#713943", "#8b4652", "#ffffff"),
        }
        fg, hover, txt = styles[kind]
        height = kwargs.pop("height", 38)
        return ctk.CTkButton(parent, text=text, command=command, height=height,
                             corner_radius=10, fg_color=fg, hover_color=hover,
                             text_color=txt, font=("Segoe UI", 10, "bold"), **kwargs)

    def _build_shell(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(26, 34))
        logo = ctk.CTkFrame(brand, width=42, height=42, corner_radius=13, fg_color=self.BLUE)
        logo.pack(side="left")
        logo.pack_propagate(False)
        self._label(logo, "N", 23, "#ffffff", "bold").place(relx=.5, rely=.48, anchor="center")
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", padx=11)
        self._label(brand_text, "NTSL Cores", 17, "#ffffff", "bold").pack(anchor="w")
        self._label(brand_text, "COLOR STUDIO", 8, self.MUTED, "bold").pack(anchor="w", pady=(1, 0))

        self._label(sidebar, "FERRAMENTAS", 9, "#697487", "bold").pack(anchor="w", padx=23, pady=(0, 10))
        nav_items = [
            ("rgb", "◉", "Seletor RGB", "Escolha uma cor"),
            ("native", "▦", "Cores nativas", "Constantes NTSL"),
            ("favorites", "★", "Favoritas", "Sua biblioteca"),
        ]
        for key, icon, title, subtitle in nav_items:
            btn = ctk.CTkButton(sidebar, text=f"{icon}   {title}", anchor="w",
                                height=48, corner_radius=10, fg_color="transparent",
                                hover_color="#252c39", text_color="#b9c3d2",
                                font=("Segoe UI", 12, "bold"),
                                command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", padx=13, pady=3)
            self.nav_buttons[key] = btn

        sidebar_bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        sidebar_bottom.pack(side="bottom", fill="x", padx=20, pady=20)
        ctk.CTkFrame(sidebar_bottom, height=1, fg_color=self.BORDER).pack(fill="x", pady=(0, 14))
        self._label(sidebar_bottom, "FEITO PARA INDICADORES", 8, "#697487", "bold").pack(anchor="w")
        self._label(sidebar_bottom, "NTSL · RGB · Cores nativas", 9, self.MUTED).pack(anchor="w", pady=(5, 0))

        main = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(main, fg_color=self.BG, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(23, 15))
        header.grid_columnconfigure(0, weight=1)
        self.page_title = self._label(header, "Seletor RGB", 23, "#ffffff", "bold")
        self.page_title.grid(row=0, column=0, sticky="w")
        self.page_subtitle = self._label(header, "Crie cores personalizadas para seus indicadores.", 11, self.MUTED)
        self.page_subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))
        variable = ctk.CTkFrame(header, fg_color=self.PANEL, corner_radius=12,
                                border_width=1, border_color=self.BORDER)
        variable.grid(row=0, column=1, rowspan=2, sticky="e", padx=(18, 0))
        self._label(variable, "VARIÁVEL NTSL", 8, self.MUTED, "bold").pack(anchor="w", padx=12, pady=(7, 0))
        self.variable_entry = ctk.CTkEntry(variable, textvariable=self.variable_name,
                                           width=150, height=30, border_width=0,
                                           fg_color="transparent", text_color="#ffffff",
                                           font=("Cascadia Code", 12))
        self.variable_entry.pack(padx=8, pady=(0, 6))
        self.variable_name.trace_add("write", self._on_name_change)

        self.content = ctk.CTkFrame(main, fg_color="transparent", corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew", padx=30)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        code_panel = ctk.CTkFrame(main, fg_color="#171b23", corner_radius=15,
                                  border_width=1, border_color=self.BORDER)
        code_panel.grid(row=2, column=0, sticky="ew", padx=30, pady=(14, 20))
        code_header = ctk.CTkFrame(code_panel, fg_color="transparent")
        code_header.pack(fill="x", padx=16, pady=(12, 7))
        self._label(code_header, "CÓDIGO NTSL", 10, "#e9edf5", "bold").pack(side="left")
        self._label(code_header, "PRONTO PARA USAR", 8, "#7ea9ff", "bold").pack(side="right")
        self.code = ctk.CTkTextbox(code_panel, height=138, corner_radius=9,
                                   fg_color="#10141b", text_color="#c8dcff",
                                   border_width=1, border_color="#283244",
                                   font=("Cascadia Code", 11), wrap="none")
        self.code.pack(fill="x", padx=13, pady=(0, 12))
        footer = ctk.CTkFrame(main, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 14))
        self.status = self._label(footer, "●  Pronto", 9, self.MUTED)
        self.status.pack(side="left")
        self._button(footer, "Copiar código  ↗", self._copy_code, "success", width=170).pack(side="right")

    def _page_frame(self, key):
        page = ctk.CTkFrame(self.content, fg_color="transparent", corner_radius=0)
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)
        self.pages[key] = page
        return page

    def show_page(self, key):
        for page in self.pages.values():
            page.grid_remove()
        if key in self.pages:
            self.pages[key].grid()
        for name, button in self.nav_buttons.items():
            button.configure(fg_color="#29354a" if name == key else "transparent",
                             text_color="#ffffff" if name == key else "#b9c3d2")
        titles = {
            "rgb": ("Seletor RGB", "Crie cores personalizadas para seus indicadores."),
            "native": ("Cores nativas", "Explore as constantes de cores disponíveis na linguagem NTSL."),
            "favorites": ("Paleta de favoritas", "Suas cores salvas, organizadas em uma biblioteca pessoal."),
        }
        self.page_title.configure(text=titles[key][0])
        self.page_subtitle.configure(text=titles[key][1])
        if key == "rgb":
            self.mode = "rgb"
            self._refresh_code()
        elif key == "native":
            self.mode = "native"
            self._refresh_code()

    def _build_rgb_page(self):
        page = self._page_frame("rgb")
        for column in (0, 1):
            page.grid_columnconfigure(column, weight=1, uniform="rgb")
        page.grid_rowconfigure(0, weight=1)
        preview = self._card(page)
        preview.grid(row=0, column=0, sticky="nsew", padx=(0, 9), pady=(0, 12))
        self._label(preview, "PRÉ-VISUALIZAÇÃO", 9, self.MUTED, "bold").pack(anchor="w")
        self.preview_swatch = ctk.CTkFrame(preview, height=190, corner_radius=15,
                                           fg_color="#73411e")
        self.preview_swatch.pack(fill="x", pady=(15, 16))
        self.preview_swatch.pack_propagate(False)
        self.preview_hex = self._label(preview, "#73411E", 24, "#ffffff", "bold")
        self.preview_hex.pack(anchor="w")
        self.preview_rgb = self._label(preview, "RGB  115   65   30", 11, self.MUTED)
        self.preview_rgb.pack(anchor="w", pady=(5, 0))
        self._button(preview, "Abrir seletor do sistema", self._choose_color,
                     "secondary").pack(fill="x", pady=(19, 0))

        controls = self._card(page)
        controls.grid(row=0, column=1, sticky="nsew", padx=(9, 0), pady=(0, 12))
        self._label(controls, "AJUSTE DE CANAIS", 9, self.MUTED, "bold").pack(anchor="w")
        self._label(controls, "Defina os valores RGB", 17, "#ffffff", "bold").pack(anchor="w", pady=(7, 3))
        self._label(controls, "Cada canal aceita números inteiros de 0 a 255.", 10, self.MUTED).pack(anchor="w", pady=(0, 18))
        for key, label, color in [("r", "VERMELHO", "#f06b73"),
                                  ("g", "VERDE", "#45c58a"),
                                  ("b", "AZUL", "#5798f5")]:
            row = ctk.CTkFrame(controls, fg_color="transparent")
            row.pack(fill="x", pady=(8, 13))
            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=label, text_color="#c2cad7",
                         font=("Segoe UI", 9, "bold")).pack(side="left")
            entry = ctk.CTkEntry(top, width=66, height=31, justify="center",
                                 fg_color="#12161d", border_color=self.BORDER,
                                 text_color="#ffffff", font=("Cascadia Code", 12))
            entry.pack(side="right")
            entry.insert(0, str(self.rgb[key]))
            entry.bind("<Return>", lambda e, k=key: self._entry_rgb(k))
            entry.bind("<FocusOut>", lambda e, k=key: self._entry_rgb(k))
            self.rgb_entries[key] = entry
            slider = ctk.CTkSlider(row, from_=0, to=255, number_of_steps=255,
                                   progress_color=color, button_color=color,
                                   button_hover_color=color, height=16,
                                   command=lambda value, k=key: self._slider_rgb(k, value))
            slider.pack(fill="x", pady=(9, 0))
            slider.set(self.rgb[key])
            self.rgb_sliders[key] = slider
        self._button(controls, "Adicionar às favoritas  ＋", self._quick_save_favorite,
                     "primary").pack(fill="x", pady=(9, 0))

    def _build_native_page(self):
        page = self._page_frame("native")
        page.grid_rowconfigure(1, weight=1)
        page.grid_columnconfigure(0, weight=1)
        search_card = self._card(page)
        search_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self._label(search_card, "ENCONTRE UMA CONSTANTE", 9, self.MUTED, "bold").pack(anchor="w")
        self.native_search = ctk.CTkEntry(search_card, textvariable=self.search_var,
                                          placeholder_text="Pesquisar por nome ou identificador...",
                                          height=38, fg_color="#12161d",
                                          border_color=self.BORDER)
        self.native_search.pack(fill="x", pady=(9, 0))
        self.search_var.trace_add("write", lambda *_: self._render_native_cards())
        self.native_scroll = ctk.CTkScrollableFrame(page, fg_color="transparent",
                                                    corner_radius=0)
        self.native_scroll.grid(row=1, column=0, sticky="nsew")
        for column in (0, 1, 2):
            self.native_scroll.grid_columnconfigure(column, weight=1, uniform="native")
        self.native_selected_label = self._label(page, "Selecionada: clVermelho", 10, self.MUTED)
        self.native_selected_label.grid(row=2, column=0, sticky="w", pady=(9, 0))

    def _build_favorites_page(self):
        page = self._page_frame("favorites")
        page.grid_rowconfigure(1, weight=1)
        page.grid_columnconfigure(0, weight=1)
        add = self._card(page)
        add.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self._label(add, "SALVAR COR ATUAL", 9, self.MUTED, "bold").pack(anchor="w")
        row = ctk.CTkFrame(add, fg_color="transparent")
        row.pack(fill="x", pady=(9, 0))
        self.favorite_name = tk.StringVar()
        self.favorite_entry = ctk.CTkEntry(row, textvariable=self.favorite_name,
                                           placeholder_text="Dê um nome à sua cor...",
                                           height=38, fg_color="#12161d",
                                           border_color=self.BORDER)
        self.favorite_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._button(row, "Salvar favorita  ＋", self._add_favorite, "primary",
                     width=165).pack(side="right")
        self.favorites_scroll = ctk.CTkScrollableFrame(page, fg_color="transparent",
                                                       corner_radius=0)
        self.favorites_scroll.grid(row=1, column=0, sticky="nsew")
        for column in (0, 1, 2):
            self.favorites_scroll.grid_columnconfigure(column, weight=1, uniform="fav")
        self.favorite_count = self._label(page, "0 cores salvas", 9, self.MUTED)
        self.favorite_count.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def _render_native_cards(self):
        if not hasattr(self, "native_scroll"):
            return
        for child in self.native_scroll.winfo_children():
            child.destroy()
        query = self.search_var.get().strip().lower()
        colors = [c for c in NATIVE_COLORS + EXAMPLE_COLORS
                  if query in c[0].lower() or query in c[1].lower()]
        for index, (identifier, name, color) in enumerate(colors):
            card = ctk.CTkFrame(self.native_scroll, fg_color=self.PANEL,
                                corner_radius=13, border_width=1,
                                border_color=self.BORDER)
            card.grid(row=index // 3, column=index % 3, sticky="ew",
                      padx=5, pady=5)
            card.grid_columnconfigure(1, weight=1)
            swatch = ctk.CTkFrame(card, width=43, height=43, corner_radius=10,
                                  fg_color=color)
            swatch.grid(row=0, column=0, rowspan=2, padx=11, pady=11)
            swatch.grid_propagate(False)
            ctk.CTkLabel(card, text=identifier, text_color="#f0f3f9",
                         font=("Cascadia Code", 10, "bold")).grid(
                             row=0, column=1, sticky="sw", padx=(0, 5), pady=(11, 0))
            ctk.CTkLabel(card, text=name, text_color=self.MUTED,
                         font=("Segoe UI", 9)).grid(
                             row=1, column=1, sticky="nw", padx=(0, 5), pady=(2, 11))
            card.bind("<Button-1>", lambda e, item=(identifier, name, color): self._choose_native(item))
            for widget in card.winfo_children():
                widget.bind("<Button-1>", lambda e, item=(identifier, name, color): self._choose_native(item))
            if identifier == self.selected_native[0]:
                card.configure(border_color=self.BLUE)

    def _choose_native(self, item):
        self.selected_native = item
        self.mode = "native"
        self.native_selected_label.configure(text=f"Selecionada: {item[0]}")
        self._render_native_cards()
        self._refresh_code()
        self.status.configure(text=f"●  Constante {item[0]} selecionada")

    def _render_favorites(self):
        if not hasattr(self, "favorites_scroll"):
            return
        for child in self.favorites_scroll.winfo_children():
            child.destroy()
        if not self.favorites:
            empty = self._card(self.favorites_scroll)
            empty.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
            self._label(empty, "Sua paleta ainda está vazia", 16, "#ffffff", "bold").pack(pady=(14, 5))
            self._label(empty, "Escolha uma cor no Seletor RGB e salve aqui para reutilizá-la.", 10, self.MUTED).pack(pady=(0, 14))
        for index, item in enumerate(self.favorites):
            color = self._hex(item["r"], item["g"], item["b"])
            card = ctk.CTkFrame(self.favorites_scroll, fg_color=self.PANEL,
                                corner_radius=13, border_width=1,
                                border_color=self.BLUE if index == self.selected_favorite else self.BORDER)
            card.grid(row=index // 3, column=index % 3, sticky="ew", padx=5, pady=5)
            swatch = ctk.CTkFrame(card, height=65, corner_radius=9, fg_color=color)
            swatch.pack(fill="x", padx=10, pady=(10, 8))
            ctk.CTkLabel(card, text=item["name"], text_color="#f0f3f9",
                         font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=11)
            ctk.CTkLabel(card, text=f'RGB {item["r"]}, {item["g"]}, {item["b"]}  ·  {color.upper()}',
                         text_color=self.MUTED, font=("Cascadia Code", 8)).pack(anchor="w", padx=11, pady=(3, 8))
            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.pack(fill="x", padx=9, pady=(0, 10))
            self._button(actions, "Aplicar", lambda i=index: self._apply_favorite(i),
                         "success", width=90, height=30).pack(side="left", expand=True, fill="x", padx=(0, 4))
            self._button(actions, "Excluir", lambda i=index: self._delete_favorite(i),
                         "danger", width=75, height=30).pack(side="left", expand=True, fill="x", padx=(4, 0))
        self.favorite_count.configure(text=f"{len(self.favorites)} cores salvas")

    def _valid_name(self):
        name = self.variable_name.get().strip()
        return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) else None

    def _rgb_code(self):
        name = self._valid_name()
        if not name:
            return "// Informe um nome de variável válido."
        r, g, b = self.rgb["r"], self.rgb["g"], self.rgb["b"]
        return (f"var\n  {name} : integer;\n\nbegin\n"
                "  // RGB(Vermelho, Verde, Azul)\n"
                "  // Números inteiros entre 0 e 255\n"
                f"  {name} := RGB({r},{g},{b});\n\nend;")

    def _native_code(self):
        name = self._valid_name()
        if not name:
            return "// Informe um nome de variável válido."
        return (f"var\n  {name} : integer;\n\nbegin\n\n"
                f"  // Cor {self.selected_native[1].lower()} nativa\n"
                f"  {name} := {self.selected_native[0]};\n\nend;")

    def _refresh_code(self):
        text = self._rgb_code() if self.mode == "rgb" else self._native_code()
        self.code.configure(state="normal")
        self.code.delete("1.0", "end")
        self.code.insert("1.0", text)
        self.code.configure(state="disabled")

    def _on_name_change(self, *_):
        if hasattr(self, "code"):
            self._refresh_code()

    def _refresh_rgb(self):
        color = self._hex(self.rgb["r"], self.rgb["g"], self.rgb["b"])
        self.preview_swatch.configure(fg_color=color)
        self.preview_hex.configure(text=color.upper())
        self.preview_rgb.configure(text=f'RGB   {self.rgb["r"]}   {self.rgb["g"]}   {self.rgb["b"]}')
        for key in ("r", "g", "b"):
            if key in self.rgb_entries:
                self.rgb_entries[key].delete(0, "end")
                self.rgb_entries[key].insert(0, str(self.rgb[key]))
            if key in self.rgb_sliders:
                self.rgb_sliders[key].set(self.rgb[key])
        self._refresh_code()

    def _slider_rgb(self, key, value):
        if self._syncing:
            return
        self.rgb[key] = int(round(float(value)))
        self.mode = "rgb"
        self._refresh_rgb()

    def _entry_rgb(self, key):
        try:
            value = int(self.rgb_entries[key].get())
            if not 0 <= value <= 255:
                raise ValueError
        except ValueError:
            self.rgb_entries[key].delete(0, "end")
            self.rgb_entries[key].insert(0, str(self.rgb[key]))
            return
        self.rgb[key] = value
        self.mode = "rgb"
        self._refresh_rgb()

    def _choose_color(self):
        result = colorchooser.askcolor(color=self._hex(**self.rgb), title="Selecionar cor RGB", parent=self)
        if result and result[0]:
            self.rgb = dict(zip(("r", "g", "b"), (int(round(v)) for v in result[0])))
            self.mode = "rgb"
            self._refresh_rgb()

    def _quick_save_favorite(self):
        self.show_page("favorites")
        self.favorite_entry.focus_set()
        self.status.configure(text="●  Dê um nome à cor e clique em Salvar favorita.")

    def _add_favorite(self):
        name = self.favorite_name.get().strip()
        if not name:
            messagebox.showwarning("Nome necessário", "Digite um nome para esta cor.", parent=self)
            return
        item = {"name": name, **self.rgb}
        existing = next((i for i, fav in enumerate(self.favorites)
                         if (fav["r"], fav["g"], fav["b"]) == (item["r"], item["g"], item["b"])), None)
        if existing is None:
            self.favorites.append(item)
            self.selected_favorite = len(self.favorites) - 1
        else:
            self.favorites[existing] = item
            self.selected_favorite = existing
        if self._save_favorites():
            self.favorite_name.set("")
            self._render_favorites()
            self.status.configure(text=f'●  Favorita "{name}" salva.')

    def _apply_favorite(self, index):
        item = self.favorites[index]
        self.rgb = {k: item[k] for k in ("r", "g", "b")}
        self.mode = "rgb"
        self.show_page("rgb")
        self._refresh_rgb()
        self.status.configure(text=f'●  Cor "{item["name"]}" aplicada ao seletor RGB.')

    def _delete_favorite(self, index):
        item = self.favorites[index]
        if not messagebox.askyesno("Excluir favorita", f'Deseja excluir "{item["name"]}"?', parent=self):
            return
        del self.favorites[index]
        self.selected_favorite = None
        if self._save_favorites():
            self._render_favorites()
            self.status.configure(text=f'●  Cor "{item["name"]}" excluída.')

    def _copy_code(self):
        if not self._valid_name():
            messagebox.showwarning("Nome inválido",
                                   "Use letras, números ou _ e não comece com número.", parent=self)
            return
        text = self.code.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.status.configure(text="●  Código copiado para a área de transferência.")


def main():
    app = NTSLCoresApp()
    app.mainloop()


if __name__ == "__main__":
    main()
