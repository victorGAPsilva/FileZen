import os
import shutil
import time
from datetime import datetime
from pathlib import Path

class FileOrganizer:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.extensions_map = self._build_extensions_map()

    def _build_extensions_map(self):
        """Inverte o dicionário de configuração para mapear extensão -> categoria."""
        ext_map = {}
        for category, extensions in self.config.get("extensions", {}).items():
            for ext in extensions:
                ext_map[ext.lower()] = category
        return ext_map

    def get_user_folder_path(self, folder_name):
        """Resolve caminhos de pastas do usuário como Downloads/Documentos."""
        user_home = Path.home()
        
        # mapeamento comum de pastas em inglês/português
        common_folders = {
            "Downloads": user_home / "Downloads",
            "Documents": user_home / "Documents",
            "Documentos": user_home / "Documents",
            "Desktop": user_home / "Desktop",
            "Área de Trabalho": user_home / "Desktop",
            "Pictures": user_home / "Pictures",
            "Imagens": user_home / "Pictures",
            "Videos": user_home / "Videos",
            "Vídeos": user_home / "Videos",
            "Music": user_home / "Music",
            "Músicas": user_home / "Music"
        }
        
        path = common_folders.get(folder_name)
        if path and path.exists():
            return path
            
        # Tenta caminho absoluto se não for uma pasta padrão
        if os.path.exists(folder_name):
            return Path(folder_name)
            
        return None

    def get_destination_folder(self, base_folder, category, file_path):
        """Determina a pasta de destino, criando subpastas se necessário."""
        organizados_name = self.config.get("destination_folder", "Organizados")
        dest_path = base_folder / organizados_name / category
        
        if self.config.get("organize_by_date"):
            # Adiciona subpasta de Ano-Mês
            file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            date_folder = file_date.strftime("%Y-%m")
            dest_path = dest_path / date_folder

        if not dest_path.exists():
            try:
                os.makedirs(dest_path)
            except Exception as e:
                self.logger.log_error(f"Não foi possível criar pasta {dest_path}: {e}")
                return None
                
        return dest_path

    def get_unique_filename(self, destination, filename):
        """Garante que não sobrescreva arquivos existentes, adicionando (1), (2), etc."""
        if not (destination / filename).exists():
            return filename
            
        name, ext = os.path.splitext(filename)
        counter = 1
        while (destination / f"{name} ({counter}){ext}").exists():
            counter += 1
        
        return f"{name} ({counter}){ext}"

    def process_file(self, file_path, base_folder):
        """Processa um único arquivo."""
        try:
            # Ignora arquivos de sistema ou temporários
            if file_path.name.startswith('.') or file_path.name.startswith('~') or file_path.name == "desktop.ini":
                return

            # Ignora o próprio arquivo de log e arquivos do script se estiverem na pasta
            if "filezen" in file_path.name.lower():
                return

            category = self.extensions_map.get(file_path.suffix.lower())
            
            if not category:
                # Opcional: mover 'Outros' ou ignorar
                return 

            destination_dir = self.get_destination_folder(base_folder, category, file_path)
            if not destination_dir:
                return

            new_filename = self.get_unique_filename(destination_dir, file_path.name)
            destination_path = destination_dir / new_filename

            # Verificação de arquivo em uso (tentativa simples)
            try:
                shutil.move(str(file_path), str(destination_path))
                self.logger.log_move(file_path.name, str(base_folder), str(destination_dir))
            except PermissionError:
                self.logger.log_error(f"Permissão negada ou arquivo em uso: {file_path.name}")
            except Exception as e:
                self.logger.log_error(f"Erro ao mover {file_path.name}: {e}")

        except Exception as e:
            self.logger.log_error(f"Erro processando {file_path}: {e}")

    def run_scan(self):
        """Executa uma varredura nas pastas configuradas."""
        self.logger.log_info("Iniciando verificação de arquivos...")
        
        folders_to_scan = self.config.get("monitored_folders", [])
        
        for folder_name in folders_to_scan:
            path = self.get_user_folder_path(folder_name)
            
            if not path:
                self.logger.log_error(f"Pasta não encontrada ou inválida: {folder_name}")
                continue

            self.logger.log_info(f"Verificando: {path}")
            
            try:
                # Lista apenas arquivos no topo (não recursivo para evitar bagunça profunda)
                # A menos que seja desejado recursividade, mas MVP geralmente e raiz da pasta.
                for item in path.iterdir():
                    if item.is_file():
                        self.process_file(item, path)
            except Exception as e:
                self.logger.log_error(f"Erro ao acessar pasta {path}: {e}")

        self.logger.log_info("Verificação concluída.")
