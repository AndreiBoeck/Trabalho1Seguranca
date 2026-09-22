# Vigenere Lab

Aplicação em Python para criptografar arquivos com a cifra de Vigenère e
recuperar a chave por criptoanálise, assumindo textos em português.

A interface principal abre no navegador e funciona localmente no computador.
Inclui tema escuro, animações sincronizadas, seleção de arquivos, relatório
da análise e botão para abrir o resultado.

## Requisitos

- Python **3.9 ou superior**, com suporte a `venv` e `pip`.
- Um navegador instalado e uma sessão gráfica.
- Permissão de escrita na pasta do projeto.

Não há dependências externas: os arquivos necessários estão neste repositório,
e a instalação não precisa baixar pacotes. O Python deve ser instalado
previamente. A interface no navegador não exige Tkinter.

## Instalação

Baixe o projeto em **Code → Download ZIP** e extraia todos os arquivos,
ou clone o repositório:

```bash
git clone https://github.com/AndreiBoeck/Trabalho1Seguranca.git
cd Trabalho1Seguranca
```

### macOS

Dê dois cliques em `instalar_macos.command` ou execute no Terminal,
dentro da pasta extraída:

```bash
bash instalar_macos.command
```

### Linux

Abra um terminal na pasta extraída:

```bash
bash instalar_linux.sh
```

No Debian/Ubuntu, pode ser necessário instalar o pacote `python3-venv`.
O botão de abrir arquivos usa `xdg-open`, do pacote `xdg-utils`.

### Windows

Dê dois cliques em `instalar_windows.bat` ou execute no Prompt de Comando:

```bat
instalar_windows.bat
```

Ao instalar Python, marque **Add Python to PATH** e reabra o terminal.

### O que os instaladores fazem

1. Verificam a versão do Python e os arquivos essenciais.
2. Criam a pasta `.venv`, caso não exista.
3. Usam o Python e as variáveis do ambiente virtual para iniciar o programa.
4. Verificam `requirements.txt`, que não tem pacotes externos.
5. Iniciam o servidor local e abrem o navegador padrão.

Execute o mesmo instalador nas próximas vezes: a `.venv` será reutilizada.
A ativação vale para o processo do programa e não altera permanentemente
seu terminal. Não copie a `.venv` entre computadores ou sistemas operacionais.

Para preparar sem abrir a interface:

```bash
python3 instalar.py --preparar
```

No Windows, use `py -3 instalar.py --preparar`.

## Como usar

### Criptografar

1. Abra a aba **Cifrar**.
2. Clique em **Procurar arquivo…** ou digite o caminho de um `.txt` em UTF-8.
3. Digite a chave, exibida em texto claro.
4. Informe o nome ou caminho do arquivo de saída.
5. Clique em **Criptografar arquivo**.
6. Use **Abrir arquivo gerado** para visualizar o resultado.

### Quebrar a cifra

1. Abra a aba **Quebrar cifra**.
2. Selecione ou informe o arquivo criptografado.
3. Defina o arquivo de saída.
4. Escolha o tamanho máximo da chave a testar (padrão: 10).
5. Clique em **Quebrar criptografia**. Não é necessário informar a senha.
6. Confira o relatório e abra o arquivo gerado.

O relatório apresenta os ICs calculados, o candidato escolhido, o tamanho
estimado e a chave recuperada. Também mostra amostras dos subtextos, as três
frequências predominantes por coluna, os deslocamentos e o qui-quadrado.
A prévia exibe até 900 caracteres; o arquivo contém o texto decifrado completo.

### Caminhos de arquivos

Digitar apenas `meu_texto.txt` procura esse arquivo na pasta de
`vigenere_web.py`. A mesma regra vale para a saída: `resultado.txt` será
salvo nessa pasta. Caminhos absolutos também são aceitos.

O seletor permite escolher entradas em outras pastas, mas isso não altera
a pasta padrão de saída.

**Use uma saída diferente da entrada:** arquivos existentes no caminho de
saída são sobrescritos.

### Animações

As linhas de entrada, chave e resultado preenchem o card e rolam juntas para
a esquerda. Na quebra, primeiro aparecem o gráfico de IC e a chave inferida.
A sequência de quebra dura aproximadamente 15 segundos, além do processamento,
dependendo da chave e do navegador.

Ative **Pular animação** para obter o resultado assim que o cálculo terminar.
As animações demonstram resultados já calculados; sua duração não mede o
tempo de execução do algoritmo.

### Encerrar e reabrir

Mantenha o terminal aberto durante o uso. Pressione **Ctrl+C** nesse terminal
para encerrar o servidor. Fechar somente a aba do navegador não encerra o
programa. Para reabrir, execute novamente o instalador.

O endereço padrão é `http://127.0.0.1:8765/interface.html`. Se a porta estiver
ocupada, outra porta local será escolhida; o endereço aparecerá no terminal
e será aberto automaticamente.

## Demonstração com Dom Casmurro

O projeto inclui o texto fornecido de *Dom Casmurro*, de Machado de Assis,
com o cabeçalho e demais conteúdos do Project Gutenberg.

| Campo | Valor |
| --- | --- |
| Original | `exemplo_original.txt` |
| Chave usada | `segredo` |
| Exemplo cifrado | `exemplo_criptografado.txt` |
| Limite de tamanho para o teste | `10` |
| Chave esperada na quebra | `segredo` |
| Tamanho esperado | `7` |
| Letras após higienização | `308887` |

Para demonstrar, abra **Quebrar cifra** e execute com os valores padrão.
O início do resultado está em inglês por causa do cabeçalho do Project
Gutenberg; o romance vem depois.

## Funcionamento dos algoritmos

### Higienização

O texto é convertido para minúsculas e normalizado com Unicode NFD.
São mantidas apenas letras de `a` a `z`, removendo acentos, espaços,
pontuação e números. A chave recebe o mesmo tratamento e precisa conter
pelo menos uma letra válida.

### Cifra de Vigenère

Cada letra equivale a um número de `a = 0` até `z = 25`. A chave se
repete ciclicamente ao longo da mensagem:

```text
Cifrar:   C[i] = (P[i] + K[i mod tamanho_da_chave]) mod 26
Decifrar: P[i] = (C[i] - K[i mod tamanho_da_chave]) mod 26
```

### Criptoanálise

Para cada tamanho candidato, o texto é dividido em colunas e calcula-se a
média dos Índices de Coincidência:

```text
IC = soma(f * (f - 1)) / (N * (N - 1))
```

`f` é a quantidade de ocorrências de uma letra e `N` é o tamanho da coluna.
O maior IC médio indica o tamanho candidato.

Em cada coluna, os 26 deslocamentos são comparados à distribuição típica
do português por qui-quadrado. O menor custo determina a letra da chave.
Repetições exatas na chave inferida são reduzidas ao menor período.
Os deslocamentos inversos reconstroem o texto higienizado.

### Limitações

A quebra é estatística e pode estimar uma chave incorreta. Textos longos e
naturais em português tendem a funcionar melhor que textos curtos, outros
idiomas ou conteúdos com frequências incomuns. A análise exige ao menos
40 letras e testa somente até o limite escolhido na interface.

Espaços, acentos e pontuação removidos não são recuperáveis. O resultado
preserva a sequência de letras, sem a formatação original. Arquivos grandes
são processados em memória; o consumo cresce com o tamanho da entrada.

## Arquivos do projeto

| Arquivo | Finalidade |
| --- | --- |
| `instalar_macos.command` | Instalação e abertura no macOS |
| `instalar_linux.sh` | Instalação e abertura no Linux |
| `instalar_windows.bat` | Instalação e abertura no Windows |
| `instalar.py` | Preparação compartilhada da venv e inicialização |
| `requirements.txt` | Dependências (sem pacotes externos) |
| `vigenere_web.py` | Servidor local e operações com arquivos |
| `interface.html` | Interface principal, animações e relatório |
| `vigenere_core.py` | Algoritmos com comentários essenciais |
| `exemplo_original.txt` | Dom Casmurro para demonstração |
| `exemplo_criptografado.txt` | Exemplo cifrado com segredo |

## Execução manual

Execute na pasta do projeto, depois de preparar o ambiente.

**macOS/Linux:**

```bash
.venv/bin/python vigenere_web.py
```

**Windows (Prompt de Comando):**

```bat
.venv\Scripts\python.exe vigenere_web.py
```

## Solução de problemas

| Problema | Solução |
| --- | --- |
| Python não encontrado | Instale Python 3.9+ e reabra o terminal; no Windows, confira o PATH. |
| Windows: Unable to create process usando um caminho como C:\\Python314\\python.exe | O launcher aponta para um Python ausente. Atualize o instalador, que testa alternativas funcionais. Se nenhuma existir, instale ou repare Python com Add Python to PATH. |
| Falha ao criar venv no Linux | Verifique o suporte a venv; no Debian/Ubuntu, confira o pacote python3-venv. |
| Venv incompleta ou de outro sistema | Encerre o programa, renomeie a pasta .venv e execute novamente o instalador. |
| Arquivo essencial ausente | Extraia o ZIP completo, mantendo os arquivos juntos. |
| Navegador não abriu | Abra manualmente o endereço impresso no terminal. |
| Entrada não encontrada | Confira o caminho; nomes sem pasta usam a pasta do programa. |
| Erro de codificação | Salve a entrada como texto UTF-8. |
| Saída não pode ser gravada | Escolha uma pasta com permissão de escrita. |
| Arquivo não abre no Linux | Verifique xdg-open e um aplicativo associado a .txt. |
| Chave estimada incorreta | Use texto maior em português e confira o limite de tamanho da chave. |

O instalador foi executado no macOS. Windows e Linux ainda precisam de
validação nos respectivos sistemas.
