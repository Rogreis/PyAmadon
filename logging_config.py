"""
Configuração avançada de logging para a aplicação Amadon
Similar ao log4net, permite configuração flexível dos logs
"""
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


class AmadonLoggingConfig:
    """Configurador de logging para a aplicação Amadon"""
    
    @staticmethod
    def setup_advanced_logging(logger_name='Amadon', log_level=logging.DEBUG):
        """
        Configura um sistema de logging avançado
        
        Args:
            logger_name (str): Nome do logger
            log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            logging.Logger: Logger configurado
        """
        
        # Cria o logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        
        # Remove handlers existentes
        if logger.handlers:
            logger.handlers.clear()
        
        # Cria diretório de logs se não existir
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # 1. Handler para arquivo principal (todos os logs)
        main_file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'amadon.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_file_handler.setLevel(logging.DEBUG)
        main_file_handler.setFormatter(detailed_formatter)
        
        # 2. Handler para erros apenas
        error_file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'amadon_errors.log',
            maxBytes=5*1024*1024,   # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(detailed_formatter)
        
        # 3. Handler para console (apenas INFO e acima)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # 4. Handler para arquivo diário
        daily_handler = logging.handlers.TimedRotatingFileHandler(
            log_dir / 'amadon_daily.log',
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(detailed_formatter)
        
        # Adiciona os handlers
        logger.addHandler(main_file_handler)
        logger.addHandler(error_file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(daily_handler)
        
        # Evita propagação para o logger raiz
        logger.propagate = False
        
        return logger
    
    @staticmethod
    def get_logger_with_context(logger_name, context):
        """
        Cria um logger com contexto específico
        
        Args:
            logger_name (str): Nome base do logger
            context (str): Contexto adicional (ex: 'UI', 'Database', 'FileIO')
        
        Returns:
            logging.Logger: Logger com contexto
        """
        return logging.getLogger(f"{logger_name}.{context}")


# Níveis de log personalizados (como no log4net)
def setup_custom_levels():
    """Adiciona níveis de log personalizados"""
    
    # Nível TRACE (mais detalhado que DEBUG)
    TRACE_LEVEL = 5
    logging.addLevelName(TRACE_LEVEL, "TRACE")
    
    def trace(self, message, *args, **kwargs):
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, message, args, **kwargs)
    
    logging.Logger.trace = trace
    
    # Nível FATAL (mais crítico que ERROR)
    FATAL_LEVEL = 60
    logging.addLevelName(FATAL_LEVEL, "FATAL")
    
    def fatal(self, message, *args, **kwargs):
        if self.isEnabledFor(FATAL_LEVEL):
            self._log(FATAL_LEVEL, message, args, **kwargs)
    
    logging.Logger.fatal = fatal


# Configuração de exemplo
if __name__ == "__main__":
    # Configura níveis personalizados
    setup_custom_levels()
    
    # Cria logger avançado
    config = AmadonLoggingConfig()
    logger = config.setup_advanced_logging()
    
    # Testa todos os níveis
    logger.trace("Mensagem de TRACE - nível mais detalhado")
    logger.debug("Mensagem de DEBUG")
    logger.info("Mensagem de INFO")
    logger.warning("Mensagem de WARNING") 
    logger.error("Mensagem de ERROR")
    logger.fatal("Mensagem de FATAL - erro crítico")
    
    print("Logs de teste criados! Verifique a pasta 'logs/'")