import os


def get_root_dir() -> str:
    """
    Return the absolute path of the root directory of the project.
    @return: Absolute path of the root directory.
    """
    return os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def get_env() -> str:
    """
    Returns the absolute path to the .env.
    """
    return os.path.join(get_root_dir(), "config/.env")
