__author__ = 'KotenkoAlex'

import os
import sys
import logging.config

import server

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Set defaults
if not server.PROJECT_PATH:
    server.PROJECT_PATH = project_root
if not server.LOG_PATH:
    server.LOG_PATH = os.path.join(project_root, 'runtime', 'app.log')
if not server.API_DOCUMENT_ROOT:
    server.API_DOCUMENT_ROOT = os.path.join(project_root, 'api')
if not server.WWW_DOCUMENT_ROOT:
    server.WWW_DOCUMENT_ROOT = os.path.join(project_root, 'www')
if not server.HISTORY_DOCUMENT_ROOT:
    server.HISTORY_DOCUMENT_ROOT = os.path.join(project_root, 'api', 'history')

# Set up logging
log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'nice': {
            'format': '%(asctime)s %(name)s [%(levelname)s] :: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'nice',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': server.LOG_PATH,
            'level': 'WARNING',
            'formatter': 'nice',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
logging.config.dictConfig(log_config)
