import json
import time
import os
import sys
from pathlib import Path

# Adiciona o diretório atual ao path para importações
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger import Logger
from organizer import FileOrganizer

CONFIG_FILE = "config.json"

def load_config():
    """Carrega as configurações ou cria padrão se não existir."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CONFIG_FILE)
    
    default_config = {
        "monitored_folders": ["Downloads", "Documents"],
        "destination_folder": "Organizados",
        "scan_interval_seconds": 60,
        "organize_by_date": False,
        "extensions": {
            "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "Documentos": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"],
            "Videos": [".mp4", ".mov", ".avi"],
            "Audio": [".mp3", ".wav"],
            "Compactados": [".zip", ".rar"]
        }
    }

    if not os.path.exists(config_path):
        return default_config
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler config.json: {e}. Usando padrão.")
        return default_config

def main():
    # Inicializa Logger
    # Log dir sobe um nível do src
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    logger = Logger(log_dir)
    
    logger.log_info("FileZen iniciado - Seu Organizador Digital")

    # Loop principal
    while True:
        try:
            config = load_config()
            organizer = FileOrganizer(config, logger)
            
            organizer.run_scan()
            
            interval = config.get("scan_interval_seconds", 60)
            # logger.log_info(f"Dormindo por {interval} segundos...") # Opcional reduzir log
            time.sleep(interval)
            
        except KeyboardInterrupt:
            logger.log_info("FileZen parando pelo usuário.")
            break
        except Exception as e:
            logger.log_error(f"Erro crítico no loop principal: {e}")
            time.sleep(60) # Espera antes de tentar de novo em caso de erro

if __name__ == "__main__":
    main()
