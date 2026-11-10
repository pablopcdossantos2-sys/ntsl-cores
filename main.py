"""
NTSL Cores - Seletor RGB para indicadores NTSL
Aplicativo desktop feito apenas com a biblioteca padrão do Python.
"""

import re
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk


class NTSLCoresApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NTSL Cores | Seletor RGB")
        self.root.geometry("570x650")
        self.root.minsize(500, 600)
        self.root.configure(bg="#202124")

        self.values = {"r": 115, "g": 65, "b": 30}
        self.variable_name = tk.StringVar(value="cor")
        self.rgb_vars = {
            "r": tk.IntVar(value=self.values["r"]),
            "g": tk.IntVar(value=self.values["g"]),
            "b": tk.IntVar(value=self.values["b"]),
        }
        self.hex_var = tk.StringVar()
        self.hex_entry_var = tk.StringVar()
        self._updating = False

        self._build_ui()
        self._refresh_color()

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "RGB.Horizontal.TScale",
            background="#202124",
            troughcolor="#45474a",
        )

        header = tk.Frame(self.root, bg="#292a2d", padx=20, pady=16)
        header.pack(fill="x")
        tk.Label(
            header, text="NTSL CORES", bg="#292a2d", fg="#ffffff",
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w")
        tk.Label(
            header, text="Seletor de cores RGB para indicadores",
            bg="#292a2d", fg="#b9bbbe", font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(3, 0))

        main = tk.Frame(self.root, bg="#202124", padx=22, pady=18)
        main.pack(fill="both", expand=True)

        tk.Label(
            main, text="COR SELECIONADA", bg="#202124", fg="#b9bbbe",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        preview_row = tk.Frame(main, bg="#202124")
        preview_row.pack(fill="x", pady=(8, 18))
        self.preview = tk.Canvas(
            preview_row, width=110, height=72, bg="#ffffff",
            highlightthickness=1, highlightbackground="#55585c"
        )
        self.preview.pack(side="left")
        self.preview_rect = self.preview.create_rectangle(
            0, 0, 110, 72, fill="#73411e", outline=""
        )
        tk.Button(
            preview_row, text="Escolher cor...", command=self._choose_color,
            bg="#3b82f6", fg="white", activebackground="#2563eb",
            activeforeground="white", relief="flat", padx=16, pady=9,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        ).pack(side="left", padx=14)

        tk.Label(
            main, text="AJUSTE RGB", bg="#202124", fg="#b9bbbe",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.scale_widgets = {}
        channel_info = [
            ("r", "Vermelho", "#ef4444"),
            ("g", "Verde", "#22c55e"),
            ("b", "Azul", "#3b82f6"),
        ]
        for key, label, accent in channel_info:
            line = tk.Frame(main, bg="#202124")
            line.pack(fill="x", pady=5)
            tk.Label(
                line, text=label, width=11, anchor="w",
                bg="#202124", fg="#e8eaed", font=("Segoe UI", 10)
            ).pack(side="left")
            scale = tk.Scale(
                line, from_=0, to=255, orient="horizontal",
                variable=self.rgb_vars[key], command=self._on_scale,
                showvalue=False, resolution=1, length=300,
                bg="#202124", fg="#e8eaed", troughcolor="#45474a",
                activebackground=accent, highlightthickness=0,
                bd=0, sliderlength=18
            )
            scale.pack(side="left", fill="x", expand=True, padx=8)
            value_label = tk.Label(
                line, text="0", width=4, anchor="e",
                bg="#202124", fg="#ffffff", font=("Consolas", 11, "bold")
            )
            value_label.pack(side="right")
            self.scale_widgets[key] = (scale, value_label)

        tk.Label(
            main, text="CÓDIGO HEXADECIMAL", bg="#202124", fg="#b9bbbe",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(18, 6))
        hex_row = tk.Frame(main, bg="#202124")
        hex_row.pack(fill="x")
        tk.Entry(
            hex_row, textvariable=self.hex_entry_var, state="readonly",
            readonlybackground="#303236", fg="#ffffff",
            font=("Consolas", 12), relief="flat", bd=0
        ).pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        tk.Button(
            hex_row, text="Copiar HEX", command=self._copy_hex,
            bg="#45474a", fg="white", relief="flat", padx=12, pady=8,
            cursor="hand2"
        ).pack(side="right")

        tk.Label(
            main, text="NOME DA VARIÁVEL NTSL", bg="#202124", fg="#b9bbbe",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(20, 6))
        tk.Entry(
            main, textvariable=self.variable_name, bg="#303236",
            fg="#ffffff", insertbackground="white", relief="flat",
            font=("Consolas", 12)
        ).pack(fill="x", ipady=9)

        tk.Label(
            main, text="CÓDIGO GERADO", bg="#202124", fg="#b9bbbe",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(20, 6))
        self.code_text = tk.Text(
            main, height=7, bg="#171819", fg="#d7e3fc",
            insertbackground="white", relief="flat",
            font=("Consolas", 11), padx=12, pady=10,
            wrap="none"
        )
        self.code_text.pack(fill="both", expand=True)

        footer = tk.Frame(main, bg="#202124")
        footer.pack(fill="x", pady=(12, 0))
        tk.Button(
            footer, text="Copiar código NTSL", command=self._copy_code,
            bg="#16a34a", fg="white", activebackground="#15803d",
            activeforeground="white", relief="flat", padx=16, pady=10,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        ).pack(side="right")
        tk.Label(
            footer, text="Valores RGB: inteiros de 0 a 255",
            bg="#202124", fg="#9aa0a6", font=("Segoe UI", 8)
        ).pack(side="left")

        self.variable_name.trace_add("write", self._refresh_code)

    def _choose_color(self):
        initial = self._rgb_to_hex()
        chosen = colorchooser.askcolor(
            color=initial, title="Selecionar cor RGB", parent=self.root
        )
        if chosen and chosen[0]:
            red, green, blue = (int(round(v)) for v in chosen[0])
            self._set_rgb(red, green, blue)

    def _on_scale(self, _value=None):
        if self._updating:
            return
        self.values = {key: int(var.get()) for key, var in self.rgb_vars.items()}
        self._refresh_color()

    def _set_rgb(self, red, green, blue):
        self._updating = True
        self.values = {"r": red, "g": green, "b": blue}
        for key, value in self.values.items():
            self.rgb_vars[key].set(value)
        self._updating = False
        self._refresh_color()

    def _rgb_to_hex(self):
        return "#{:02x}{:02x}{:02x}".format(
            self.values["r"], self.values["g"], self.values["b"]
        )

    def _refresh_color(self):
        color = self._rgb_to_hex()
        self.preview.itemconfigure(self.preview_rect, fill=color)
        self.hex_entry_var.set(color.upper())
        for key, value in self.values.items():
            self.scale_widgets[key][1].configure(text=str(value))
        self._refresh_code()

    def _refresh_code(self, *_args):
        name = self.variable_name.get().strip()
        valid = bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))
        red, green, blue = self.values["r"], self.values["g"], self.values["b"]

        if valid:
            code = (
                "var\n"
                f"  {name} : integer;\n"
                "\n"
                "begin\n"
                "  // RGB(Vermelho, Verde, Azul)\n"
                "  // Números inteiros entre 0 e 255\n"
                f"  {name} := RGB({red},{green},{blue});"
            )
        else:
            code = "Informe um nome de variável válido.\nUse letras, números e _; não comece com número."

        self.code_text.configure(state="normal")
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", code)
        self.code_text.configure(state="disabled")

    def _copy(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def _copy_hex(self):
        self._copy(self._rgb_to_hex().upper())

    def _copy_code(self):
        name = self.variable_name.get().strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            messagebox.showwarning(
                "Nome inválido",
                "Informe um nome de variável válido antes de copiar.",
                parent=self.root,
            )
            return
        self._copy(self.code_text.get("1.0", "end-1c"))
        messagebox.showinfo(
            "Código copiado",
            "O código NTSL foi copiado para a área de transferência.",
            parent=self.root,
        )


def main():
    root = tk.Tk()
    NTSLCoresApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
