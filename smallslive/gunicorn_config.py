# gunicorn_config.py

# Bind to all interfaces on port 8000
bind = "0.0.0.0:8000"

# Number of worker processes (adjust based on your CPU)
workers = 3

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"