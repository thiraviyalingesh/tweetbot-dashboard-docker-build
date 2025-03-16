import logging

def setup_logger(name=None):
    # Clear the info.log file at the beginning of the session
    open('dataframe.log', 'w').close()
    # Create a custom logger
    logger = logging.getLogger(name)

    # Set level to DEBUG to capture all levels of logs
    logger.setLevel(logging.DEBUG)

    # Create handlers
    # Handler for DEBUG logs (append mode)
    debug_handler = logging.FileHandler('debug.log', mode='a',encoding='utf-8')
    # Handler for INFO logs (write mode)
    info_handler = logging.FileHandler('info.log', mode='a',encoding='utf-8')
    # Handler for DataFrame logs (append mode)
    df_handler = logging.FileHandler('dataframe.log', mode='a',encoding='utf-8')

    # Set log levels for each handler
    debug_handler.setLevel(logging.DEBUG)
    info_handler.setLevel(logging.INFO)
    df_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
    debug_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)
    df_handler.setFormatter(formatter)

    # Add handlers to the logger only if not already added
    if not logger.handlers:
        logger.addHandler(debug_handler)
        logger.addHandler(info_handler)
        logger.addHandler(df_handler)

    return logger

def log_dataframe(logger, df, operation_name):
    """Helper function to log DataFrame information"""
    logger.debug(f"\n{'='*50}")
    logger.debug(f"DataFrame Operation: {operation_name}")
    logger.debug(f"Shape: {df.shape}")
    logger.debug(f"Columns: {list(df.columns)}")
    logger.debug(f"Data Types:\n{df.dtypes}")
    logger.debug(f"First few rows:\n{df.head()}")
    logger.debug(f"{'='*50}\n")
