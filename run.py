import tornado.web
import tornado.ioloop

from config.application import Application

import os
from app.utils.constants import Environment


if __name__ == "__main__":
    print('\n--------------------- Starting Central Authentication System (CAS) ---------------------')

    environment = os.environ.get(Environment.KEY, None)
    print(f"{Environment.KEY} = {environment}")
    if environment is None: raise ImportError("Environment is not defined")
    environment = environment.lower()
    if environment not in [Environment.DEVELOPMENT, Environment.QC, Environment.PRODUCTION]: raise ImportError("Invalid environment name")
    print(f"{Environment.KEY} = {environment}")

    app = Application().initialize(environment)

    # Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    # C:\Apache24\conf\httdp.conf
    # C:\Apache24\bin\httpd.exe
    # C:\Windows\System32\drivers\etc\hosts
    # /user/(?P<action>create|list|profile|edit|delete)
    # netstat -ano | findstr :<port_number>
    # taskkill /F /PID <process_pid>

    print(f"\nServer is live")
    tornado.ioloop.IOLoop.instance().start()