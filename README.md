# 🛠️ Lançador de Notas - App de Automação

Aplicativo desenvolvido em **Python** com **Selenium** para automatizar o lançamento de notas extraídas do sistema **TarefaSP** para a plataforma **Sala do Futuro**, da Secretaria da Educação de SP.

---

## 📋 Requisitos

- Windows com **Google Chrome** instalado
- Python 3.10 ou superior (somente para rodar pelo código-fonte)
- Conta de professor com acesso à SED e ao Sala do Futuro

---

## 📦 Instalação

### Opção 1 — Usar o executável (recomendado)

Baixe o `LancaNotas.exe` na página de releases e execute direto, sem precisar instalar nada.

### Opção 2 — Rodar pelo código-fonte

1. Clone o repositório:
   ```bash
   git clone https://github.com/Marc0x6f/auto_tarefas.git
   cd auto_tarefas
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```bash
   python app_gui.py
   ```

---

## 🗂️ Exportando o CSV da SED

Antes de usar o app, é necessário exportar a planilha de notas da SED:

1. Acesse a **SED** e vá em:
   `Centro de Mídias → Tarefas → Relatório de Atividades do CMSP`

2. Clique em **"Gerar Excel"** e selecione a opção:
   `Arquivo CSV sem formatação`

3. Salve o arquivo. O nome não precisa seguir um padrão específico.

> O CSV exportado usa vírgula como separador e contém uma coluna chamada `atividade` com as notas de 0 a 10. Alunos sem nota nessa coluna são ignorados automaticamente.

---

## 🚀 Como usar o aplicativo

### Passo 1 — Abrir o Chrome em modo conectado

Clique no botão **"Abrir Chrome (modo conectado)"**.

- O app abre o Chrome com uma porta de depuração especial (`9222`) que permite controlar o navegador automaticamente.
- **Importante:** feche todas as janelas do Chrome antes de clicar nesse botão. Se o Chrome já estiver aberto, o app vai avisar.
- Aguarde o Chrome carregar completamente antes de continuar.

### Passo 2 — Acessar a página de lançamento de notas

No Chrome que foi aberto, acesse o **Sala do Futuro** e navegue até a página de lançamento das avaliações da turma desejada. O app precisa que essa aba esteja aberta e visível.

> A página correta tem o título **"Lançamento das Avaliações"** na aba do navegador.

### Passo 3 — Selecionar o CSV

Clique em **"Selecionar CSV (Planilha de Notas)"** e escolha o arquivo exportado da SED.

### Passo 4 — Iniciar o lançamento

Clique em **"Iniciar Lançamento"**. O app vai:

1. Ler e processar o CSV automaticamente
2. Conectar ao Chrome já aberto
3. Para cada aluno com nota, buscar o nome na tabela do site
4. Preencher o campo de nota e passar para o próximo
5. Ao final, ajustar a visualização para 100 alunos por página

O log na parte inferior da janela mostra em tempo real o que está acontecendo.

---

## 🧪 Testar o CSV sem lançar notas

Antes de rodar o lançamento real, você pode verificar exatamente quais alunos e quais notas serão enviados usando o script de teste:

```bash
python testar_csv.py caminho/para/arquivo.csv
```

A saída mostra uma tabela com o nome como será buscado no site e a nota que será preenchida:

```
#    Nome (buscado no site)                   Nota enviada
--------------------------------------------------------------
1    FERNANDO COELHO PELLEGRINO               10,0
2    JOABE CHIARATTI DE MORAES                10,0
...
--------------------------------------------------------------

Total de alunos que receberao nota: 8
```

---

## ⚠️ Pontos de atenção

- **Não mexa no mouse nem no teclado** enquanto o lançamento estiver em andamento. O Selenium controla o navegador e qualquer interferência pode travar o processo.
- Alunos com o campo `atividade` **vazio** no CSV são ignorados — a nota não é lançada para eles.
- O app busca o aluno pelo nome **sem acentos**. Se o nome no site estiver muito diferente do CSV, o aluno vai aparecer como não encontrado no log.
- O Chrome precisa ter sido aberto **pelo próprio app** (modo debug). Se abrir o Chrome manualmente, a conexão não vai funcionar.

---

## 🔧 Build (gerar o .exe)

Para gerar um novo executável a partir do código-fonte:

```bash
python -m PyInstaller --name "LancaNotas" --onefile --noconsole --icon=icone.ico app_gui.py
```

O arquivo gerado estará em `dist/LancaNotas.exe`.

---

## 🧰 Tecnologias utilizadas

- [Python 3](https://www.python.org/)
- [Selenium](https://www.selenium.dev/) — automação do navegador
- [Pandas](https://pandas.pydata.org/) — leitura e processamento do CSV
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — interface gráfica
- [PyInstaller](https://pyinstaller.org/) — empacotamento como `.exe`
