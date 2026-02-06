import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        log_filename = datetime.now().strftime("filezen_%Y-%m-%d.log")
        self.log_file = os.path.join(self.log_dir, log_filename)
        
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def log_info(self, message):
        """Registra uma mensagem informativa."""
        print(f"[INFO] {message}")
        logging.info(message)

    def log_error(self, message):
        """Registra uma mensagem de erro."""
        print(f"[ERRO] {message}")
        logging.error(message)

    def log_move(self, filename, source, destination):
        """Registra a movimentação de um arquivo."""
        msg = f"Movido: '{filename}' de '{source}' para '{destination}'"
        print(f"[SUCESSO] {msg}")
        logging.info(msg)
