import multiprocessing

bind = "0.0.0.0:8000"

chdir = "/app"

workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 50
keepalive = 5

loglevel = 'info'
accesslog = "-"
errorlog = "-"
capture_output = True
