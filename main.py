"""
NTSL Cores - seletor RGB, cores nativas e paleta de favoritas.
Requer Python 3.9+ e Tkinter. Não utiliza dependências externas.
"""
import json
import os
import re
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, messagebox, ttk

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
    ("clRed", "Vermelho (exemplo do manual)", "#ff0000"),
    ("clGreen", "Verde (exemplo do manual)", "#008000"),
    ("clWhite", "Branco (exemplo do manual)", "#ffffff"),
    ("clYellow", "Amarelo (exemplo do manual)", "#ffff00"),
]


def favorites_file():
    """Retorna um caminho gravável e persistente para a paleta do usuário."""
    base = os.environ.get("APPDATA")
    folder = Path(base) / "NTSLCores" if base else Path.home() / ".ntsl-cores"
    return folder / "favorites.json"


class NTSLCoresApp:
    BG = "#202124"
    PANEL = "#292a2d"
    FIELD = "#303236"
    FG = "#f1f3f4"
    MUTED = "#b9bbbe"

    def __init__(self, root):
        self.root = root
        root.title("NTSL Cores")
        root.geometry("760x790")
        root.minsize(650, 700)
        root.configure(bg=self.BG)

        self.variable_name = tk.StringVar(value="cor")
        self.rgb = {"r": 115, "g": 65, "b": 30}
        self.rgb_vars = {k: tk.IntVar(value=v) for k, v in self.rgb.items()}
        self.selected_native = NATIVE_COLORS[16]
        self.mode = "rgb"
        self._syncing = False
        self.favorites_path = favorites_file()
        self.favorites = self._load_favorites()

        self._build()
        self._refresh_rgb()
        self._refresh_native_code()
        self._populate_favorites()

    def _load_favorites(self):
        try:
            with self.favorites_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                return []
            valid = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name", "")).strip()
                try:
                    r, g, b = (int(item[k]) for k in ("r", "g", "b"))
                except (KeyError, TypeError, ValueError):
                    continue
                if name and all(0 <= v <= 255 for v in (r, g, b)):
                    valid.append({"name": name, "r": r, "g": g, "b": b})
            return valid
        except (OSError, json.JSONDecodeError):
            return []

    def _save_favorites(self):
        try:
            self.favorites_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.favorites_path.with_suffix(".tmp")
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(self.favorites, file, ensure_ascii=False, indent=2)
            temp_path.replace(self.favorites_path)
            return True
        except OSError as exc:
            messagebox.showerror(
                "Não foi possível salvar",
                f"A paleta não pôde ser gravada no computador.\n\n{exc}",
                parent=self.root,
            )
            return False

    def _setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TNotebook", background=self.BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure("TNotebook.Tab", background="#25282d", foreground="#aeb6c2",
                        padding=(20, 12), font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", "#343a43")],
                  foreground=[("selected", "#ffffff")])
        style.configure("TScrollbar", background="#343a43", troughcolor=self.BG,
                        bordercolor=self.BG, arrowcolor="#aeb6c2")
        style.configure("TScale", background=self.PANEL)
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(12, 8))
        style.configure("Accent.TButton", background="#4f8cff", foreground="#ffffff",
                        borderwidth=0, padding=(14, 9))
        style.map("Accent.TButton", background=[("active", "#3977e8")])
        style.configure("Success.TButton", background="#1f9d70", foreground="#ffffff",
                        borderwidth=0, padding=(14, 9))
        style.map("Success.TButton", background=[("active", "#17845d")])
        style.configure("Danger.TButton", background="#8f3d49", foreground="#ffffff",
                        borderwidth=0, padding=(12, 8))
        style.map("Danger.TButton", background=[("active", "#a44855")])

    def _card(self, parent, padding=16):
        return tk.Frame(parent, bg=self.PANEL, padx=padding, pady=padding,
                        highlightthickness=1, highlightbackground="#353a42",
                        highlightcolor="#353a42")

    def _section_title(self, parent, title, subtitle=None):
        tk.Label(parent, text=title, bg=self.PANEL, fg=self.FG,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(parent, text=subtitle, bg=self.PANEL, fg=self.MUTED,
                     font=("Segoe UI", 9), wraplength=650,
                     justify="left").pack(anchor="w", pady=(4, 0))

    def _build(self):
        self._setup_styles()
        self.root.title("NTSL Cores")
        self.root.geometry("900x860")
        self.root.minsize(760, 760)
        self.root.configure(bg=self.BG)

        # Cabeçalho
        header = tk.Frame(self.root, bg="#171a20", padx=26, pady=18,
                          highlightthickness=0)
        header.pack(fill="x")
        brand = tk.Frame(header, bg="#171a20")
        brand.pack(side="left", fill="x", expand=True)
        mark = tk.Canvas(brand, width=42, height=42, bg="#171a20",
                         highlightthickness=0)
        mark.pack(side="left", padx=(0, 12))
        mark.create_oval(3, 3, 39, 39, fill="#4f8cff", outline="")
        mark.create_oval(11, 11, 31, 31, fill="#171a20", outline="")
        mark.create_oval(17, 17, 25, 25, fill="#4f8cff", outline="")
        title_box = tk.Frame(brand, bg="#171a20")
        title_box.pack(side="left", anchor="center")
        tk.Label(title_box, text="NTSL Cores", bg="#171a20", fg="#ffffff",
                 font=("Segoe UI", 19, "bold")).pack(anchor="w")
        tk.Label(title_box, text="UTILITÁRIO DE CORES PARA INDICADORES",
                 bg="#171a20", fg="#8d99aa",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(header, text="RGB  •  NATIVAS  •  FAVORITAS",
                 bg="#252b35", fg="#b9c9e2", padx=12, pady=8,
                 font=("Segoe UI", 8, "bold")).pack(side="right")

        body = tk.Frame(self.root, bg=self.BG, padx=24, pady=20)
        body.pack(fill="both", expand=True)

        # Identificador da variável
        variable_card = self._card(body, 14)
        variable_card.pack(fill="x", pady=(0, 14))
        row = tk.Frame(variable_card, bg=self.PANEL)
        row.pack(fill="x")
        label_box = tk.Frame(row, bg=self.PANEL)
        label_box.pack(side="left", fill="x", expand=True)
        tk.Label(label_box, text="VARIÁVEL DE DESTINO", bg=self.PANEL, fg="#8f9aaa",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(label_box, text="Nome usado no código do indicador",
                 bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))
        self.variable_name = tk.StringVar(value="cor")
        entry = tk.Entry(row, textvariable=self.variable_name, bg="#20242b", fg="#ffffff",
                         insertbackground="#ffffff", selectbackground="#416fb8",
                         relief="flat", font=("Consolas", 12), width=24,
                         highlightthickness=1, highlightbackground="#414956",
                         highlightcolor="#4f8cff")
        entry.pack(side="right", ipady=9, ipadx=10)
        self.variable_name.trace_add("write", self._on_name_change)

        # Navegação principal
        self.tabs = ttk.Notebook(body)
        self.tabs.pack(fill="both", expand=True)
        self.rgb_tab = tk.Frame(self.tabs, bg=self.BG, padx=4, pady=16)
        self.native_tab = tk.Frame(self.tabs, bg=self.BG, padx=4, pady=16)
        self.favorites_tab = tk.Frame(self.tabs, bg=self.BG, padx=4, pady=16)
        self.tabs.add(self.rgb_tab, text="  ◉  Seletor RGB  ")
        self.tabs.add(self.native_tab, text="  ◈  Cores nativas  ")
        self.tabs.add(self.favorites_tab, text="  ★  Favoritas  ")
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._build_rgb_tab()
        self._build_native_tab()
        self._build_favorites_tab()

        # Painel fixo do código gerado
        result = tk.Frame(body, bg="#171a20", padx=16, pady=13,
                          highlightthickness=1, highlightbackground="#353d49")
        result.pack(fill="x", pady=(14, 0))
        result_head = tk.Frame(result, bg="#171a20")
        result_head.pack(fill="x", pady=(0, 9))
        tk.Label(result_head, text="CÓDIGO NTSL", bg="#171a20", fg="#ffffff",
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(result_head, text="PRONTO PARA COPIAR", bg="#202b39", fg="#8db9ff",
                 padx=9, pady=4, font=("Segoe UI", 7, "bold")).pack(side="right")
        self.code = tk.Text(result, height=7, bg="#101318", fg="#c9ddff",
                            insertbackground="#ffffff", relief="flat",
                            font=("Cascadia Code", 10), padx=13, pady=11,
                            wrap="none", borderwidth=0,
                            highlightthickness=1, highlightbackground="#303946")
        self.code.pack(fill="x")
        bottom = tk.Frame(body, bg=self.BG)
        bottom.pack(fill="x", pady=(10, 0))
        self.status = tk.Label(bottom, text="●  Pronto para copiar para o indicador.",
                               bg=self.BG, fg="#8f9aaa", font=("Segoe UI", 8))
        self.status.pack(side="left")
        ttk.Button(bottom, text="Copiar código NTSL  ↗", command=self._copy_code,
                   style="Success.TButton").pack(side="right")

    def _build_rgb_tab(self):
        tab = self.rgb_tab
        preview_card = self._card(tab, 18)
        preview_card.pack(fill="x", pady=(0, 12))
        self._section_title(preview_card, "Cor selecionada",
                            "Ajuste os canais RGB ou abra o seletor visual do sistema.")
        preview_row = tk.Frame(preview_card, bg=self.PANEL)
        preview_row.pack(fill="x", pady=(16, 2))
        self.rgb_preview = tk.Canvas(preview_row, width=150, height=104,
                                     highlightthickness=1, highlightbackground="#515966",
                                     bg="#73411e")
        self.rgb_preview.pack(side="left")
        self.rgb_swatch = self.rgb_preview.create_rectangle(
            0, 0, 150, 104, fill="#73411e", outline="")
        info = tk.Frame(preview_row, bg=self.PANEL)
        info.pack(side="left", fill="both", expand=True, padx=18)
        tk.Label(info, text="VALORES DA COR", bg=self.PANEL, fg="#8f9aaa",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.rgb_values_label = tk.Label(info, text="", bg=self.PANEL, fg="#ffffff",
                                         font=("Consolas", 16, "bold"))
        self.rgb_values_label.pack(anchor="w", pady=(7, 3))
        self.hex_label = tk.Label(info, text="", bg=self.PANEL, fg="#aab6c7",
                                  font=("Consolas", 10))
        self.hex_label.pack(anchor="w")
        ttk.Button(info, text="Abrir seletor de cores", command=self._choose_color,
                   style="Accent.TButton").pack(anchor="w", pady=(14, 0))

        controls = self._card(tab, 18)
        controls.pack(fill="both", expand=True)
        self._section_title(controls, "Ajuste fino", "Cada canal aceita valores inteiros de 0 a 255.")
        self.scale_labels = {}
        for key, label, accent in [("r", "VERMELHO", "#ef6464"),
                                   ("g", "VERDE", "#4ac58a"),
                                   ("b", "AZUL", "#5798f5")]:
            line = tk.Frame(controls, bg=self.PANEL)
            line.pack(fill="x", pady=(15, 3))
            tk.Label(line, text=label, width=12, anchor="w", bg=self.PANEL,
                     fg="#b5c0cf", font=("Segoe UI", 8, "bold")).pack(side="left")
            tk.Scale(line, from_=0, to=255, orient="horizontal",
                     variable=self.rgb_vars[key], command=self._on_rgb_change,
                     showvalue=False, resolution=1, bg=self.PANEL, fg=self.FG,
                     troughcolor="#424a56", activebackground=accent,
                     highlightthickness=0, bd=0, sliderlength=22,
                     relief="flat").pack(side="left", fill="x", expand=True, padx=12)
            val = tk.Label(line, text="0", width=4, bg="#20242b", fg="#ffffff",
                           padx=5, pady=4, font=("Consolas", 11, "bold"))
            val.pack(side="right")
            self.scale_labels[key] = val

    def _build_native_tab(self):
        tab = self.native_tab
        card = self._card(tab, 18)
        card.pack(fill="both", expand=True)
        self._section_title(card, "Biblioteca de cores nativas",
                            "Selecione uma constante para gerar a atribuição correspondente no código NTSL.")
        search_row = tk.Frame(card, bg=self.PANEL)
        search_row.pack(fill="x", pady=(16, 12))
        tk.Label(search_row, text="⌕", bg=self.PANEL, fg="#8fa0b5",
                 font=("Segoe UI", 16)).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._populate_native_list())
        search = tk.Entry(search_row, textvariable=self.search_var, bg="#20242b", fg="#ffffff",
                          insertbackground="#ffffff", relief="flat",
                          font=("Segoe UI", 10), highlightthickness=1,
                          highlightbackground="#414956", highlightcolor="#4f8cff")
        search.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        tk.Label(card, text="CONSTANTE                         NOME DA COR",
                 bg=self.PANEL, fg="#7f8b9c", font=("Segoe UI", 8, "bold")
                 ).pack(anchor="w", pady=(0, 6))
        list_frame = tk.Frame(card, bg="#20242b", highlightthickness=1,
                              highlightbackground="#414956")
        list_frame.pack(fill="both", expand=True)
        self.native_list = tk.Listbox(list_frame, bg="#20242b", fg="#e5eaf1",
                                      selectbackground="#294a75", selectforeground="#ffffff",
                                      font=("Consolas", 10), activestyle="none",
                                      relief="flat", height=11, exportselection=False,
                                      borderwidth=0, highlightthickness=0,
                                      selectborderwidth=0)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.native_list.yview)
        self.native_list.configure(yscrollcommand=scroll.set)
        self.native_list.pack(side="left", fill="both", expand=True, padx=8, pady=7)
        scroll.pack(side="right", fill="y")
        self.native_list.bind("<<ListboxSelect>>", self._select_native)
        selected = tk.Frame(card, bg="#20242b", padx=12, pady=10)
        selected.pack(fill="x", pady=(12, 0))
        self.native_preview = tk.Canvas(selected, width=48, height=38, bg="#ff0000",
                                        highlightthickness=0)
        self.native_preview.pack(side="left")
        self.native_preview_rect = self.native_preview.create_rectangle(
            0, 0, 48, 38, fill="#ff0000", outline="")
        self.native_description = tk.Label(selected, text="", bg="#20242b", fg="#dce5f2",
                                           font=("Segoe UI", 10, "bold"))
        self.native_description.pack(side="left", padx=12)
        self._populate_native_list()

    def _build_favorites_tab(self):
        tab = self.favorites_tab
        card = self._card(tab, 18)
        card.pack(fill="both", expand=True)
        self._section_title(card, "Sua paleta pessoal",
                            "Guarde cores usadas com frequência e reutilize-as em diferentes indicadores.")
        save_row = tk.Frame(card, bg=self.PANEL)
        save_row.pack(fill="x", pady=(16, 12))
        self.favorite_name = tk.StringVar()
        entry = tk.Entry(save_row, textvariable=self.favorite_name, bg="#20242b",
                         fg="#ffffff", insertbackground="#ffffff", relief="flat",
                         font=("Segoe UI", 10), highlightthickness=1,
                         highlightbackground="#414956", highlightcolor="#4f8cff")
        entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
        entry.insert(0, "")
        ttk.Button(save_row, text="＋  Salvar cor atual", command=self._add_favorite,
                   style="Accent.TButton").pack(side="right")

        tk.Label(card, text="CORES SALVAS", bg=self.PANEL, fg="#7f8b9c",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(3, 7))
        list_frame = tk.Frame(card, bg="#20242b", highlightthickness=1,
                              highlightbackground="#414956")
        list_frame.pack(fill="both", expand=True)
        self.favorites_list = tk.Listbox(
            list_frame, bg="#20242b", fg="#e5eaf1", selectbackground="#294a75",
            selectforeground="#ffffff", font=("Consolas", 10), activestyle="none",
            relief="flat", height=9, exportselection=False, borderwidth=0,
            highlightthickness=0, selectborderwidth=0
        )
        fav_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                                   command=self.favorites_list.yview)
        self.favorites_list.configure(yscrollcommand=fav_scroll.set)
        self.favorites_list.pack(side="left", fill="both", expand=True, padx=8, pady=7)
        fav_scroll.pack(side="right", fill="y")
        self.favorites_list.bind("<<ListboxSelect>>", self._select_favorite)

        details = tk.Frame(card, bg="#20242b", padx=12, pady=10)
        details.pack(fill="x", pady=(12, 0))
        self.favorite_preview = tk.Canvas(details, width=54, height=42, bg="#73411e",
                                           highlightthickness=0)
        self.favorite_preview.pack(side="left")
        self.favorite_preview_rect = self.favorite_preview.create_rectangle(
            0, 0, 54, 42, fill="#73411e", outline="")
        self.favorite_details = tk.Label(details, text="Selecione uma cor da lista.",
                                          bg="#20242b", fg="#c2ccda",
                                          font=("Segoe UI", 9), justify="left")
        self.favorite_details.pack(side="left", padx=12)

        actions = tk.Frame(card, bg=self.PANEL)
        actions.pack(fill="x", pady=(14, 0))
        ttk.Button(actions, text="Aplicar cor selecionada", command=self._apply_favorite,
                   style="Success.TButton").pack(side="left")
        ttk.Button(actions, text="Excluir", command=self._delete_favorite,
                   style="Danger.TButton").pack(side="left", padx=9)

    def _populate_favorites(self, select_index=None):
        self.favorites_list.delete(0, "end")
        for item in self.favorites:
            hex_color = self._hex(item["r"], item["g"], item["b"])
            self.favorites_list.insert(
                "end",
                f'{item["name"]}   |   RGB({item["r"]}, {item["g"]}, {item["b"]})   |   {hex_color.upper()}'
            )
        if select_index is not None and 0 <= select_index < len(self.favorites):
            self.favorites_list.selection_set(select_index)
            self.favorites_list.activate(select_index)
            self.favorites_list.see(select_index)
            self._show_favorite_details(select_index)
        elif not self.favorites:
            self.favorite_details.configure(text="Nenhuma cor favorita salva ainda.")
            self.favorite_preview.itemconfigure(self.favorite_preview_rect, fill=self.FIELD)

    def _favorite_index(self):
        selection = self.favorites_list.curselection()
        return selection[0] if selection else None

    def _show_favorite_details(self, index):
        item = self.favorites[index]
        hex_color = self._hex(item["r"], item["g"], item["b"])
        self.favorite_preview.itemconfigure(self.favorite_preview_rect, fill=hex_color)
        self.favorite_details.configure(
            text=f'{item["name"]} — RGB({item["r"]}, {item["g"]}, {item["b"]}) — {hex_color.upper()}'
        )

    def _select_favorite(self, _event=None):
        index = self._favorite_index()
        if index is not None:
            self._show_favorite_details(index)

    def _add_favorite(self):
        name = self.favorite_name.get().strip()
        if not name:
            messagebox.showwarning("Nome necessário", "Digite um nome para identificar esta cor.",
                                   parent=self.root)
            return
        item = {"name": name, "r": self.rgb["r"], "g": self.rgb["g"], "b": self.rgb["b"]}
        # Evita entradas idênticas; se o RGB já existir, atualiza seu rótulo.
        existing = next((i for i, fav in enumerate(self.favorites)
                         if (fav["r"], fav["g"], fav["b"]) ==
                            (item["r"], item["g"], item["b"])), None)
        if existing is None:
            self.favorites.append(item)
            index = len(self.favorites) - 1
        else:
            self.favorites[existing] = item
            index = existing
        if self._save_favorites():
            self._populate_favorites(index)
            self.favorite_name.set("")
            self.status.configure(text=f'Cor favorita "{name}" salva.')

    def _apply_favorite(self):
        index = self._favorite_index()
        if index is None:
            messagebox.showinfo("Selecione uma cor", "Escolha uma cor favorita na lista.",
                                parent=self.root)
            return
        item = self.favorites[index]
        self._set_rgb(item["r"], item["g"], item["b"])
        self.mode = "rgb"
        self.tabs.select(self.rgb_tab)
        self._refresh_rgb()
        self.status.configure(text=f'Cor favorita "{item["name"]}" aplicada ao seletor RGB.')

    def _delete_favorite(self):
        index = self._favorite_index()
        if index is None:
            messagebox.showinfo("Selecione uma cor", "Escolha uma cor favorita para excluir.",
                                parent=self.root)
            return
        item = self.favorites[index]
        if not messagebox.askyesno("Confirmar exclusão",
                                   f'Deseja excluir a cor favorita "{item["name"]}"?',
                                   parent=self.root):
            return
        del self.favorites[index]
        if self._save_favorites():
            next_index = min(index, len(self.favorites) - 1)
            self._populate_favorites(next_index if next_index >= 0 else None)
            self.status.configure(text=f'Cor favorita "{item["name"]}" excluída.')

    @staticmethod
    def _hex(r, g, b):
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def _all_native(self):
        return NATIVE_COLORS + EXAMPLE_COLORS

    def _populate_native_list(self):
        query = self.search_var.get().strip().lower()
        self.visible_native = [c for c in self._all_native()
                               if query in c[0].lower() or query in c[1].lower()]
        self.native_list.delete(0, "end")
        for name, description, _ in self.visible_native:
            self.native_list.insert("end", f"{name:<18}  {description}")
        selected = next((i for i, c in enumerate(self.visible_native)
                         if c[0] == self.selected_native[0]), None)
        if selected is not None:
            self.native_list.selection_set(selected)
            self.native_list.see(selected)

    def _select_native(self, _event=None):
        selection = self.native_list.curselection()
        if not selection:
            return
        self.selected_native = self.visible_native[selection[0]]
        name, description, color = self.selected_native
        self.native_preview.itemconfigure(self.native_preview_rect, fill=color)
        self.native_description.configure(text=f"{name} — {description}")
        self._refresh_native_code()
        if self.tabs.index("current") == 1:
            self.mode = "native"
            self._show_code(self._native_code())

    def _on_tab_changed(self, _event=None):
        index = self.tabs.index("current")
        if index == 0:
            self.mode = "rgb"
            self._show_code(self._rgb_code())
        elif index == 1:
            self.mode = "native"
            self._show_code(self._native_code())
        else:
            # A aba Favoritas não muda a origem do código gerado.
            self._refresh_code_for_mode()

    def _on_name_change(self, *_):
        self._refresh_code_for_mode()

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
        constant = self.selected_native[0]
        return (f"var\n  {name} : integer;\n\nbegin\n\n"
                f"  // Cor {self.selected_native[1].lower()} nativa\n"
                f"  {name} := {constant};\n\nend;")

    def _show_code(self, text):
        self.code.configure(state="normal")
        self.code.delete("1.0", "end")
        self.code.insert("1.0", text)
        self.code.configure(state="disabled")

    def _refresh_native_code(self):
        self._refresh_code_for_mode()

    def _refresh_code_for_mode(self):
        self._show_code(self._rgb_code() if self.mode == "rgb" else self._native_code())

    def _refresh_rgb(self):
        hex_color = self._rgb_hex()
        self.rgb_preview.itemconfigure(self.rgb_swatch, fill=hex_color)
        for k, v in self.rgb.items():
            self.scale_labels[k].configure(text=str(v))
        self.rgb_values_label.configure(
            text=f"RGB({self.rgb['r']}, {self.rgb['g']}, {self.rgb['b']})")
        self.hex_label.configure(text=f"HEX {hex_color.upper()}")
        self._refresh_code_for_mode()

    def _on_rgb_change(self, _value=None):
        if self._syncing:
            return
        self.rgb = {k: int(v.get()) for k, v in self.rgb_vars.items()}
        self.mode = "rgb"
        self._refresh_rgb()

    def _rgb_hex(self):
        return self._hex(self.rgb["r"], self.rgb["g"], self.rgb["b"])

    def _set_rgb(self, red, green, blue):
        self._syncing = True
        self.rgb = {"r": int(red), "g": int(green), "b": int(blue)}
        for key, value in self.rgb.items():
            self.rgb_vars[key].set(value)
        self._syncing = False
        self._refresh_rgb()

    def _choose_color(self):
        chosen = colorchooser.askcolor(color=self._rgb_hex(), title="Selecionar cor RGB",
                                       parent=self.root)
        if chosen and chosen[0]:
            values = [int(round(x)) for x in chosen[0]]
            self._set_rgb(*values)
            self.mode = "rgb"
            self.tabs.select(self.rgb_tab)
            self._refresh_rgb()

    def _copy_code(self):
        if not self._valid_name():
            messagebox.showwarning("Nome inválido",
                                   "Use letras, números ou _ e não comece com número.",
                                   parent=self.root)
            return
        text = self.code.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.status.configure(text="Código copiado para a área de transferência.")


def main():
    root = tk.Tk()
    NTSLCoresApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
