import tornado.web
import tornado.ioloop

from config.application import Application
from app import settings

import os
from app.utils.constants import Environment


if __name__ == "__main__":
    print('\n--------------------- Starting Central Authentication System (CAS) ---------------------')

    environment = os.environ.get(Environment.KEY, None)
    print(f"{Environment.KEY} = {environment}")
    if environment is None: raise ImportError("Environment is not defined")
    environment = environment.lower()
    print(f"{Environment.KEY} = {environment}")

    app = Application().initialize(environment)

    if environment == Environment.DEVELOPMENT:
        port  = settings.PORT
        app.listen(port)

    # Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    # C:\Apache24\conf
    # C:\Apache24\bin\httpd.exe
    # C:\Windows\System32\drivers\etc\hosts
    # /user/(?P<action>create|list|profile|edit|delete)
    print(f"\nServer is live")
    tornado.ioloop.IOLoop.instance().start()