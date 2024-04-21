import logging


def get_logger(name: str):
    """
    Get a logger with the specified name.

    This function configures the logging module with a basic configuration that includes a format for the log messages,
    a log level, and a date format. It then returns a logger with the specified name.

    Parameters:
    :param name: The name of the logger.

    Returns:
    :return logging.Logger: A logger with the specified name.
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(name)
