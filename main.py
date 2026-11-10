"""
NTSL Cores - seletor de cores RGB e constantes nativas NTSL.
Requer Python 3.9+ e Tkinter. Não utiliza dependências externas.
"""
import re
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk

# Constantes documentadas na seção 4.7 do Manual NTSL (14/10/2026).
# Cores aproximadas apenas para visualização; o código gerado usa a constante.
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
# Identificadores vistos em exemplos do próprio manual. Mantidos separados
# da relação principal de constantes da seção 4.7.
EXAMPLE_COLORS = [
    ("clRed", "Vermelho (exemplo do manual)", "#ff0000"),
    ("clGreen", "Verde (exemplo do manual)", "#008000"),
    ("clWhite", "Branco (exemplo do manual)", "#ffffff"),
    ("clYellow", "Amarelo (exemplo do manual)", "#ffff00"),
]

class NTSLCoresApp:
    BG = "#202124"
    PANEL = "#292a2d"
    FIELD = "#303236"
    FG = "#f1f3f4"
    MUTED = "#b9bbbe"

    def __init__(self, root):
        self.root = root
        root.title("NTSL Cores")
        root.geometry("720x760")
        root.minsize(620, 680)
        root.configure(bg=self.BG)

        self.variable_name = tk.StringVar(value="cor")
        self.rgb = {"r": 115, "g": 65, "b": 30}
        self.rgb_vars = {k: tk.IntVar(value=v) for k, v in self.rgb.items()}
        self.selected_native = NATIVE_COLORS[16]
        self.mode = "rgb"
        self._syncing = False

        self._build()
        self._refresh_rgb()
        self._refresh_native_code()

    def _build(self):
        header = tk.Frame(self.root, bg=self.PANEL, padx=20, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="NTSL CORES", bg=self.PANEL, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(header, text="Seletor RGB e biblioteca de cores nativas",
                 bg=self.PANEL, fg=self.MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        body = tk.Frame(self.root, bg=self.BG, padx=18, pady=14)
        body.pack(fill="both", expand=True)

        name_row = tk.Frame(body, bg=self.BG)
        name_row.pack(fill="x", pady=(0, 10))
        tk.Label(name_row, text="Nome da variável NTSL", bg=self.BG, fg=self.MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Entry(name_row, textvariable=self.variable_name, bg=self.FIELD, fg="white",
                 insertbackground="white", relief="flat", font=("Consolas", 12)
                 ).pack(fill="x", ipady=8, pady=(5, 0))
        self.variable_name.trace_add("write", self._on_name_change)

        self.tabs = ttk.Notebook(body)
        self.tabs.pack(fill="both", expand=True)
        self.rgb_tab = tk.Frame(self.tabs, bg=self.BG, padx=16, pady=14)
        self.native_tab = tk.Frame(self.tabs, bg=self.BG, padx=16, pady=14)
        self.tabs.add(self.rgb_tab, text="  Seletor RGB  ")
        self.tabs.add(self.native_tab, text="  Cores nativas  ")
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._build_rgb_tab()
        self._build_native_tab()

        result = tk.LabelFrame(body, text=" Código NTSL gerado ", bg=self.BG, fg=self.MUTED,
                               labelanchor="nw", padx=10, pady=8)
        result.pack(fill="x", pady=(12, 0))
        self.code = tk.Text(result, height=8, bg="#171819", fg="#d7e3fc",
                            insertbackground="white", relief="flat",
                            font=("Consolas", 11), padx=10, pady=8, wrap="none")
        self.code.pack(fill="x")
        bottom = tk.Frame(body, bg=self.BG)
        bottom.pack(fill="x", pady=(10, 0))
        self.status = tk.Label(bottom, text="Pronto para copiar para o indicador.",
                               bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8))
        self.status.pack(side="left")
        tk.Button(bottom, text="Copiar código NTSL", command=self._copy_code,
                  bg="#16a34a", fg="white", activebackground="#15803d",
                  relief="flat", padx=16, pady=9, font=("Segoe UI", 10, "bold"),
                  cursor="hand2").pack(side="right")

    def _build_rgb_tab(self):
        tab = self.rgb_tab
        tk.Label(tab, text="Escolha uma cor personalizada", bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        top = tk.Frame(tab, bg=self.BG)
        top.pack(fill="x", pady=12)
        self.rgb_preview = tk.Canvas(top, width=100, height=65, highlightthickness=1,
                                     highlightbackground="#666", bg="white")
        self.rgb_preview.pack(side="left")
        self.rgb_swatch = self.rgb_preview.create_rectangle(0, 0, 100, 65,
                                                            fill="#73411e", outline="")
        tk.Button(top, text="Abrir seletor de cores...", command=self._choose_color,
                  bg="#3b82f6", fg="white", relief="flat", padx=12, pady=8,
                  cursor="hand2").pack(side="left", padx=14)

        self.scale_labels = {}
        for key, label, accent in [("r", "Vermelho", "#ef4444"),
                                   ("g", "Verde", "#22c55e"),
                                   ("b", "Azul", "#3b82f6")]:
            line = tk.Frame(tab, bg=self.BG)
            line.pack(fill="x", pady=7)
            tk.Label(line, text=label, width=11, anchor="w", bg=self.BG,
                     fg=self.FG).pack(side="left")
            tk.Scale(line, from_=0, to=255, orient="horizontal",
                     variable=self.rgb_vars[key], command=self._on_rgb_change,
                     showvalue=False, resolution=1, bg=self.BG, fg=self.FG,
                     troughcolor="#4a4d50", activebackground=accent,
                     highlightthickness=0, bd=0, sliderlength=18
                     ).pack(side="left", fill="x", expand=True, padx=8)
            val = tk.Label(line, text="0", width=4, bg=self.BG, fg="white",
                           font=("Consolas", 11, "bold"))
            val.pack(side="right")
            self.scale_labels[key] = val

        self.rgb_values_label = tk.Label(tab, text="", bg=self.BG, fg=self.MUTED,
                                         font=("Consolas", 11))
        self.rgb_values_label.pack(anchor="w", pady=(12, 0))
        self.hex_label = tk.Label(tab, text="", bg=self.BG, fg=self.MUTED,
                                  font=("Consolas", 10))
        self.hex_label.pack(anchor="w", pady=(5, 0))

    def _build_native_tab(self):
        tab = self.native_tab
        tk.Label(tab, text="Selecione uma constante nativa da NTSL",
                 bg=self.BG, fg=self.FG, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(tab, text="Amostras visuais aproximadas; o código utiliza o identificador nativo.",
                 bg=self.BG, fg=self.MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(3, 8))

        search_row = tk.Frame(tab, bg=self.BG)
        search_row.pack(fill="x", pady=(0, 8))
        tk.Label(search_row, text="Filtrar:", bg=self.BG, fg=self.MUTED).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._populate_native_list())
        tk.Entry(search_row, textvariable=self.search_var, bg=self.FIELD, fg="white",
                 insertbackground="white", relief="flat").pack(side="left", fill="x",
                                                               expand=True, padx=8, ipady=5)

        list_frame = tk.Frame(tab, bg=self.BG)
        list_frame.pack(fill="both", expand=True)
        self.native_list = tk.Listbox(list_frame, bg=self.FIELD, fg=self.FG,
                                      selectbackground="#2563eb", selectforeground="white",
                                      font=("Consolas", 10), activestyle="none",
                                      relief="flat", height=12, exportselection=False)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.native_list.yview)
        self.native_list.configure(yscrollcommand=scroll.set)
        self.native_list.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.native_list.bind("<<ListboxSelect>>", self._select_native)
        self.native_preview = tk.Canvas(tab, width=72, height=36, bg="white",
                                        highlightthickness=1, highlightbackground="#777")
        self.native_preview.pack(anchor="w", pady=(10, 4))
        self.native_preview_rect = self.native_preview.create_rectangle(
            0, 0, 72, 36, fill="#ff0000", outline="")
        self.native_description = tk.Label(tab, text="", bg=self.BG, fg=self.MUTED,
                                           font=("Segoe UI", 9))
        self.native_description.pack(anchor="w")
        self._populate_native_list()

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
        self.mode = "rgb" if self.tabs.index("current") == 0 else "native"
        self._show_code(self._rgb_code() if self.mode == "rgb" else self._native_code())

    def _on_name_change(self, *_):
        if self.mode == "rgb":
            self._show_code(self._rgb_code())
        else:
            self._show_code(self._native_code())

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
        self.rgb_values_label.configure(text=f"RGB({self.rgb['r']}, {self.rgb['g']}, {self.rgb['b']})")
        self.hex_label.configure(text=f"HEX {hex_color.upper()}")
        self._refresh_code_for_mode()

    def _on_rgb_change(self, _value=None):
        if self._syncing:
            return
        self.rgb = {k: int(v.get()) for k, v in self.rgb_vars.items()}
        self.mode = "rgb"
        self._refresh_rgb()

    def _rgb_hex(self):
        return "#{:02x}{:02x}{:02x}".format(self.rgb["r"], self.rgb["g"], self.rgb["b"])

    def _choose_color(self):
        chosen = colorchooser.askcolor(color=self._rgb_hex(), title="Selecionar cor RGB",
                                       parent=self.root)
        if chosen and chosen[0]:
            self._syncing = True
            self.rgb = dict(zip(("r", "g", "b"), (int(round(x)) for x in chosen[0])))
            for k, v in self.rgb.items():
                self.rgb_vars[k].set(v)
            self._syncing = False
            self.mode = "rgb"
            self.tabs.select(self.rgb_tab)
            self._refresh_rgb()

    def _copy_code(self):
        name = self._valid_name()
        if not name:
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
