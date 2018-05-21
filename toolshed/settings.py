BACKUP_LEVELS = {
    'daily': 14,
    'weekly': 6,
    'monthly': 6,
    'yearly': 6,
}


try:
    from .local_settings import *
except ImportError:
    pass
