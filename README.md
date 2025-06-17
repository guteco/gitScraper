# GitHub Repository Code Concatenator

Ferramenta Python para listar seus repositórios do GitHub, permitir a seleção interativa de um deles e gerar um arquivo único contendo todo o código-fonte do projeto, com estrutura de pastas, localização e detalhes de cada arquivo.

---

## ✨ Funcionalidades

- Autenticação segura via token (Personal Access Token)
- Listagem interativa dos seus repositórios (públicos e privados)
- Seleção do repositório pelo terminal
- Geração de arquivo único com:
  - Estrutura de diretórios visual
  - Conteúdo completo dos arquivos de código (.py, .js, .html, etc.)
  - Informações de localização e tamanho de cada arquivo
- Suporte a variáveis de ambiente via `.env`
- Compatível com Python 3.8+

---

## 🚀 Como Usar

### 1. Clone o repositório

git clone https://github.com/guteco/gitScraper.git

cd gitScraper

### 2. Instale as dependências

pip install -r requirements.txt

### 3. Configure seu arquivo `.env`

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

GITHUB_TOKEN=seu_token_aqui

OUTPUT_DIRECTORY=output # (opcional) Diretório para salvar os arquivos gerados

> **Dica:** Nunca compartilhe seu token. Adicione `.env` ao `.gitignore`!

### 4. Execute o script

python git-scraper.py

- O script irá listar todos os seus repositórios.
- Escolha o desejado digitando o número correspondente.
- O arquivo concatenado será salvo no diretório especificado (ou na raiz, por padrão).

---

## 🛠️ Requisitos

- Python 3.8 ou superior
- Token de acesso pessoal do GitHub (com permissão de leitura nos repositórios desejados)

---

## 📦 requirements.txt

requests==2.32.0
python-dotenv==1.0.0

---

## 📝 Exemplo de Uso

🚀 GitHub Repository Code Concatenator
🔍 Buscando seus repositórios...
✅ Encontrados 10 repositórios

🌐 meu-repo-publico

🔒 meu-repo-privado

🌐 projeto-teste
...

📋 Escolha um repositório (1-10) ou 'q' para sair: 2
✅ Repositório selecionado: meu-repo-privado

📄 Processando (1/15): src/main.py
📄 Processando (2/15): src/utils.py
...

✅ Arquivo salvo com sucesso!
📄 Nome: meu-repo-privado_concatenated_20250617_113000.txt

---

## ⚠️ Observações Importantes

- O token do GitHub é obrigatório e deve ser mantido em segredo.
- O script filtra apenas arquivos de código comuns (Python, JavaScript, HTML, etc.).
- As bibliotecas `os`, `base64`, `datetime` e `json` são da biblioteca padrão do Python.

---

## 🧩 Extensões Futuras

- Suporte a múltiplos formatos de saída (Markdown, HTML)
- Filtros por tipo de arquivo ou diretório
- Integração com Google Drive ou Dropbox para upload automático

---

## 🤝 Contribuição

Pull requests são bem-vindos! Para grandes mudanças, abra uma issue antes para discutir o que você gostaria de modificar.

---

## 📄 Licença

[MIT](LICENSE)
