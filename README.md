# NTSL Cores

Seletor de cores RGB para gerar declarações e atribuições compatíveis com indicadores NTSL.

## Requisitos

- Python 3.9 ou superior
- Tkinter (normalmente incluído na instalação padrão do Python)

Não há dependências Python externas.

## Como executar

No Windows, abra o terminal na pasta do projeto e execute:

```bash
python main.py
```

## Como usar

1. Escolha uma cor pelo botão **Escolher cor...** ou ajuste os controles Vermelho, Verde e Azul.
2. Informe o nome da variável NTSL.
3. Confira a declaração e a atribuição geradas.
4. Clique em **Copiar código NTSL** e cole no editor do indicador.

O código gerado segue este formato:

```pascal
var
  cor : integer;

begin
  // RGB(Vermelho, Verde, Azul)
  // Números inteiros entre 0 e 255
  cor := RGB(115,65,30);
```

## Portabilidade

O aplicativo usa apenas a biblioteca padrão do Python e não precisa de conexão com a internet. Para distribuir como executável Windows sem exigir Python instalado, pode-se empacotar com PyInstaller:

```bash
pyinstaller --onefile --windowed main.py
```
