import requests
import base64
import os
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

class GitHubRepoAnalyzer:
    def __init__(self, token=None):
        # Se não fornecido, buscar do .env
        if not token:
            token = os.getenv('GITHUB_TOKEN')
        
        if not token:
            raise ValueError("Token não encontrado! Verifique o arquivo .env ou forneça um token.")
        
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.selected_repo = None
    
    def get_user_repositories(self):
        """Busca todos os repositórios do usuário autenticado"""
        print("🔍 Buscando seus repositórios...")
        
        all_repos = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.base_url}/user/repos"
            params = {
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "type": "all"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Erro na resposta da API: {response.status_code}")
                print(f"Mensagem: {response.text}")
                raise Exception(f"Erro ao buscar repositórios: {response.status_code}")
            
            repos = response.json()
            if not repos:
                break
                
            all_repos.extend(repos)
            page += 1
        
        return all_repos
    
    def safe_get(self, dictionary, key, default="N/A"):
        """Função auxiliar para acessar dicionário de forma segura"""
        if dictionary is None:
            return default
        value = dictionary.get(key, default)
        return value if value is not None else default
    
    def safe_len_check(self, text, max_length=60):
        """Verifica comprimento de forma segura, tratando None"""
        if text is None or text == "N/A":
            return text
        return text[:max_length] + "..." if len(str(text)) > max_length else text
    
    def display_repositories(self, repos):
        """Exibe lista de repositórios para seleção - VERSÃO TOTALMENTE CORRIGIDA"""
        print("\n" + "="*80)
        print("📚 SEUS REPOSITÓRIOS DISPONÍVEIS")
        print("="*80)
        
        valid_repos = []
        
        for i, repo in enumerate(repos, 1):
            # Verificar se o repositório não é None
            if repo is None:
                print(f"{i:2d}. ❌ Repositório inválido (dados não disponíveis)")
                continue
            
            try:
                # Acessar campos de forma segura
                name = self.safe_get(repo, 'name', 'Nome não disponível')
                description = self.safe_get(repo, 'description', 'Sem descrição')
                language = self.safe_get(repo, 'language', 'N/A')
                
                # Campos numéricos com tratamento especial
                stars_count = repo.get('stargazers_count', 0) or 0
                updated_at = self.safe_get(repo, 'updated_at', '')
                
                # Extrair apenas a data se disponível
                updated_date = updated_at[:10] if updated_at and len(str(updated_at)) >= 10 else 'Data não disponível'
                
                # Verificar se é privado
                is_private = repo.get('private', False)
                private_icon = "🔒" if is_private else "🌐"
                
                # Estrelas visuais (máximo 5)
                stars = "⭐" * min(stars_count, 5) if stars_count > 0 else ""
                
                # URL do repositório
                html_url = self.safe_get(repo, 'html_url', 'URL não disponível')
                
                # Exibir informações - CORREÇÃO PRINCIPAL AQUI
                print(f"{i:2d}. {private_icon} {name}")
                
                # Usar safe_len_check para descrição
                desc_display = self.safe_len_check(description, 60)
                print(f"    📝 {desc_display}")
                print(f"    🔧 Linguagem: {language} | 📅 Atualizado: {updated_date}")
                
                if stars:
                    print(f"    {stars} ({stars_count} estrelas)")
                
                print(f"    🔗 {html_url}")
                print()
                
                # Adicionar à lista de repositórios válidos
                valid_repos.append(repo)
                
            except Exception as e:
                print(f"{i:2d}. ❌ Erro ao processar repositório: {str(e)}")
                print(f"    Tentando processar mesmo assim...")
                # Ainda adiciona à lista para dar opção ao usuário
                if repo is not None:
                    valid_repos.append(repo)
                continue
        
        return valid_repos
    
    def select_repository(self, repos):
        """Interface para seleção do repositório"""
        if not repos:
            print("❌ Nenhum repositório válido encontrado!")
            return None
        
        while True:
            try:
                print("="*80)
                choice = input(f"📋 Escolha um repositório (1-{len(repos)}) ou 'q' para sair: ").strip()
                
                if choice.lower() == 'q':
                    print("👋 Saindo...")
                    return None
                
                repo_index = int(choice) - 1
                
                if 0 <= repo_index < len(repos):
                    selected = repos[repo_index]
                    
                    # Verificar se o repositório selecionado é válido
                    if selected is None:
                        print("❌ Repositório inválido selecionado! Tente outro.")
                        continue
                    
                    name = self.safe_get(selected, 'name', 'Nome não disponível')
                    description = self.safe_get(selected, 'description', 'Sem descrição')
                    language = self.safe_get(selected, 'language', 'N/A')
                    
                    print(f"\n✅ Repositório selecionado: {name}")
                    print(f"📝 Descrição: {description}")
                    print(f"🔧 Linguagem principal: {language}")
                    
                    # Confirmação
                    confirm = input("\n🤔 Confirma a seleção? (s/n): ").strip().lower()
                    if confirm in ['s', 'sim', 'y', 'yes']:
                        return selected
                    else:
                        continue
                else:
                    print("❌ Número inválido! Tente novamente.")
                    
            except ValueError:
                print("❌ Por favor, digite um número válido!")
            except KeyboardInterrupt:
                print("\n👋 Operação cancelada pelo usuário.")
                return None
    
    def get_repository_tree(self, owner, repo_name):
        """Busca toda a árvore do repositório recursivamente"""
        print(f"🌳 Analisando estrutura do repositório {owner}/{repo_name}...")
        
        # Primeiro, vamos descobrir a branch padrão
        repo_url = f"{self.base_url}/repos/{owner}/{repo_name}"
        repo_response = requests.get(repo_url, headers=self.headers)
        
        if repo_response.status_code != 200:
            raise Exception(f"Erro ao acessar repositório: {repo_response.status_code}")
        
        default_branch = repo_response.json().get('default_branch', 'main')
        
        # Agora buscar a árvore
        url = f"{self.base_url}/repos/{owner}/{repo_name}/git/trees/{default_branch}"
        params = {"recursive": "1"}
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()["tree"]
        else:
            raise Exception(f"Erro ao buscar árvore: {response.status_code}")
    
    def get_file_content(self, owner, repo_name, path):
        """Busca o conteúdo de um arquivo específico"""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/contents/{path}"
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            content_data = response.json()
            if content_data["encoding"] == "base64":
                try:
                    decoded_content = base64.b64decode(content_data["content"]).decode('utf-8', errors='ignore')
                    return decoded_content
                except Exception as e:
                    print(f"⚠️  Erro ao decodificar {path}: {e}")
                    return f"// Erro ao decodificar arquivo: {e}"
        return None
    
    def filter_code_files(self, tree):
        """Filtra apenas arquivos de código"""
        code_extensions = {
            '.py', '.js', '.java', '.cpp', '.c', '.h', '.html', '.css', 
            '.php', '.rb', '.go', '.rs', '.ts', '.jsx', '.tsx', '.vue',
            '.swift', '.kt', '.scala', '.cs', '.vb', '.pl', '.r', '.m',
            '.sh', '.bat', '.ps1', '.sql', '.json', '.xml', '.yaml', '.yml'
        }
        
        code_files = []
        for item in tree:
            if item["type"] == "blob":
                _, ext = os.path.splitext(item["path"])
                if ext.lower() in code_extensions:
                    code_files.append(item)
        
        return code_files
    
    def create_directory_structure(self, files):
        """Cria um mapa da estrutura de diretórios"""
        structure = {}
        for file in files:
            path_parts = file["path"].split("/")
            current_level = structure
            
            for part in path_parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            filename = path_parts[-1]
            current_level[filename] = file
        
        return structure
    
    def format_directory_structure(self, structure, indent=0):
        """Formata a estrutura de diretórios de forma legível"""
        result = ""
        for key, value in structure.items():
            if isinstance(value, dict) and not any(isinstance(v, dict) for v in value.values()):
                result += "  " * indent + f"📄 {key}\n"
            elif isinstance(value, dict):
                result += "  " * indent + f"📁 {key}/\n"
                result += self.format_directory_structure(value, indent + 1)
        return result
    
    def process_selected_repository(self, repo):
        """Processa o repositório selecionado"""
        # Verificar se owner existe e tem login
        owner_data = repo.get('owner')
        if not owner_data or not owner_data.get('login'):
            raise Exception("Dados do proprietário do repositório não disponíveis")
        
        owner = owner_data['login']
        repo_name = self.safe_get(repo, 'name')
        
        if repo_name == "N/A":
            raise Exception("Nome do repositório não disponível")
        
        print(f"\n🚀 Iniciando processamento do repositório {owner}/{repo_name}")
        
        try:
            tree = self.get_repository_tree(owner, repo_name)
            
            print("🔍 Filtrando arquivos de código...")
            code_files = self.filter_code_files(tree)
            
            if not code_files:
                print("❌ Nenhum arquivo de código encontrado neste repositório!")
                return None, None
            
            print(f"✅ Encontrados {len(code_files)} arquivos de código")
            
            structure = self.create_directory_structure(code_files)
            
            # Informações seguras do repositório
            html_url = self.safe_get(repo, 'html_url')
            description = self.safe_get(repo, 'description')
            language = self.safe_get(repo, 'language')
            stars = repo.get('stargazers_count', 0) or 0
            forks = repo.get('forks_count', 0) or 0
            updated_at = self.safe_get(repo, 'updated_at')
            is_private = repo.get('private', False)
            
            concatenated_content = f"""# Concatenação Automática do Repositório {owner}/{repo_name}
# Repositório: {html_url}
# Descrição: {description}
# Linguagem Principal: {language}
# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Total de arquivos: {len(code_files)}

## 📊 Informações do Repositório:
- **Nome**: {repo_name}
- **Proprietário**: {owner}
- **Linguagem Principal**: {language}
- **Estrelas**: {stars}
- **Forks**: {forks}
- **Última Atualização**: {updated_at}
- **Privado**: {'Sim' if is_private else 'Não'}

## 📁 Estrutura do Repositório:
{self.format_directory_structure(structure)}

## 📄 Conteúdo dos Arquivos:
"""
            
            for i, file in enumerate(code_files, 1):
                print(f"📄 Processando ({i}/{len(code_files)}): {file['path']}")
                content = self.get_file_content(owner, repo_name, file["path"])
                
                if content:
                    concatenated_content += f"""

{'='*80}
📄 ARQUIVO: {file['path']}
📊 TAMANHO: {file['size']} bytes
📍 LOCALIZAÇÃO: /{file['path']}
{'='*80}

{content}

"""
            
            return concatenated_content, repo_name
            
        except Exception as e:
            print(f"❌ Erro ao processar repositório: {e}")
            return None, None
    
    def save_result(self, content, repo_name):
        """Salva o resultado em arquivo"""
        if not content:
            return None
        
        # Criar diretório de saída se especificado no .env
        output_dir = os.getenv('OUTPUT_DIRECTORY', '.')
        if output_dir != '.' and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        safe_repo_name = "".join(c for c in repo_name if c.isalnum() or c in ('-', '_'))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(output_dir, f"{safe_repo_name}_concatenated_{timestamp}.txt")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(filename)
            print(f"\n✅ Arquivo salvo com sucesso!")
            print(f"📄 Nome: {os.path.basename(filename)}")
            print(f"📊 Tamanho: {file_size:,} bytes")
            print(f"📍 Local: {os.path.abspath(filename)}")
            
            return filename
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            return None

def main():
    """Função principal com interface interativa"""
    print("🚀 GitHub Repository Code Concatenator v2.1 - CORRIGIDO")
    print("="*65)
    
    try:
        # Tentar carregar token do .env
        analyzer = GitHubRepoAnalyzer()
        print("✅ Token carregado do arquivo .env")
        
    except ValueError:
        # Se não encontrar no .env, solicitar manualmente
        print("⚠️  Token não encontrado no arquivo .env")
        token = input("🔑 Digite seu GitHub Personal Access Token: ").strip()
        
        if not token:
            print("❌ Token é obrigatório!")
            return
        
        analyzer = GitHubRepoAnalyzer(token)
    
    try:
        repos = analyzer.get_user_repositories()
        
        if not repos:
            print("❌ Nenhum repositório encontrado!")
            return
        
        print(f"✅ Encontrados {len(repos)} repositórios")
        
        displayed_repos = analyzer.display_repositories(repos)
        selected_repo = analyzer.select_repository(displayed_repos)
        
        if not selected_repo:
            return
        
        result, repo_name = analyzer.process_selected_repository(selected_repo)
        
        if result:
            filename = analyzer.save_result(result, repo_name)
            
            if filename:
                print(f"\n🎉 Processo concluído com sucesso!")
                print(f"📄 Arquivo disponível em: {filename}")
        else:
            print("❌ Falha no processamento do repositório")
            
    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print(f"💡 Dica: Verifique se seu token tem as permissões necessárias")

if __name__ == "__main__":
    main()
