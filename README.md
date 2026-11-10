# NTSL Cores

Aplicativo desktop para escolher cores RGB, consultar constantes nativas da linguagem NTSL e manter uma paleta pessoal de cores favoritas. Gera trechos de código prontos para colar em indicadores.

## Interface

A interface utiliza tema escuro, navegação por abas, painéis de edição, cartões de seleção e uma área fixa para visualizar o código NTSL gerado. O layout foi reorganizado para destacar a cor selecionada, facilitar o acesso às ferramentas e separar visualmente as áreas de trabalho.

## Recursos

- **Seletor RGB**: escolha por diálogo de cores ou ajuste dos canais vermelho, verde e azul (0–255).
- **Cores nativas**: lista pesquisável das constantes documentadas no Manual NTSL, com amostras visuais.
- **Paleta de favoritas**: salve cores RGB com nomes personalizados, aplique novamente ou exclua cores salvas.
- **Persistência local**: as favoritas permanecem salvas ao fechar e reabrir o programa.
- Campo para nome da variável NTSL.
- Geração automática da declaração `integer` e da atribuição RGB ou da constante nativa.
- Cópia do código completo para a área de transferência.

## Executar pelo Python

Requisitos: Python 3.9+.

```bash
python -m pip install -r requirements.txt
python main.py
```

A interface utiliza CustomTkinter e Pillow para oferecer componentes visuais modernos.

## Paleta de cores favoritas

Na aba **Favoritas**:
1. Selecione ou ajuste a cor desejada na aba **Seletor RGB**.
2. Volte à aba **Favoritas**, digite um nome e clique em **Salvar cor atual**.
3. Selecione uma cor salva e clique em **Aplicar cor selecionada** para carregá-la no seletor RGB.
4. Use **Excluir** para removê-la da paleta.

As favoritas são armazenadas em JSON no perfil local do usuário:
- Windows: `%APPDATA%\\NTSLCores\\favorites.json`
- Outros sistemas: `~/.ntsl-cores/favorites.json`

A paleta não é armazenada no executável nem sincronizada entre computadores. Para transferi-la, copie o arquivo `favorites.json` para o mesmo local no outro computador.

## Exemplo de código RGB

```pascal
var
  cor : integer;

begin
  // RGB(Vermelho, Verde, Azul)
  // Números inteiros entre 0 e 255
  cor := RGB(115,65,30);

end;
```

## Exemplo com cor nativa

```pascal
var
  cor : integer;

begin
  // Cor vermelha nativa
  cor := clVermelho;

end;
```

O aplicativo também apresenta identificadores encontrados em exemplos do manual (como `clRed`, `clGreen` e `clWhite`) em uma seção separada da relação principal da seção 4.7.

## Fonte das constantes

A relação principal de cores nativas foi transcrita da seção 4.7 (Constantes), página 14, do Manual NTSL fornecido para este projeto. As amostras hexadecimais são apenas aproximações para visualização; o aplicativo gera o identificador NTSL, não um valor RGB, ao selecionar uma constante nativa.
