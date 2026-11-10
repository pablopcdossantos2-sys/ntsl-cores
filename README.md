# NTSL Cores

Aplicativo desktop para escolher cores RGB e consultar constantes de cores nativas da linguagem NTSL, gerando o trecho de código pronto para colar em indicadores.

## Recursos

- Aba **Seletor RGB**: escolha por diálogo de cores ou ajuste dos canais vermelho, verde e azul (0–255).
- Aba **Cores nativas**: lista pesquisável das constantes documentadas no Manual NTSL, com amostra visual.
- Campo para nome da variável NTSL.
- Geração automática da declaração `integer` e da atribuição RGB ou da constante nativa.
- Cópia do código completo para a área de transferência.

## Executar pelo Python

Requisitos: Python 3.9+ com Tkinter.

```bash
python main.py
```

Não são necessárias dependências externas.

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

## Executável portátil para Windows

O GitHub Actions compila o programa em um executável Windows de arquivo único, sem janela de terminal, usando PyInstaller. O executável não exige que o usuário instale Python.

Para publicar uma versão:
1. Abra a aba **Actions** do repositório.
2. Selecione **Build and publish Windows release**.
3. Clique em **Run workflow**.
4. Informe a versão, por exemplo `v1.0.0`.
5. Após a conclusão, abra **Releases** e baixe `NTSL-Cores.exe`.

Também é possível disparar a publicação criando e enviando uma tag no formato `v*`.

## Fonte das constantes

A relação principal de cores nativas foi transcrita da seção 4.7 (Constantes), página 14, do Manual NTSL fornecido para este projeto. As amostras hexadecimais são apenas aproximações para visualização; o aplicativo gera o identificador NTSL, não um valor RGB, ao selecionar uma constante nativa.
