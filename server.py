# Import your application as:
# from wsgi import application
# Example:
from django.conf import settings
from report.wsgi import application

# Import CherryPy
import cherrypy


url=settings.STATIC_URL
root=settings.STATIC_ROOT

if __name__ == '__main__':

    """
    :param url: Relative url
    :param root: Path to static files root
    """
    config = {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': root,
        'tools.expires.on': True,
        'tools.expires.secs': 86400
    }
    cherrypy.tree.mount(None, url, {'/': config})

    # Mount the application
    cherrypy.tree.graft(application, "/")

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()


    # Configure the server object
    server.socket_host = "192.168.30.35"
    server.socket_port = 80
    server.thread_pool = 30

    # For SSL Support
    # server.ssl_module            = 'pyopenssl'
    # server.ssl_certificate       = 'ssl/certificate.crt'
    # server.ssl_private_key       = 'ssl/private.key'
    # server.ssl_certificate_chain = 'ssl/bundle.crt'

    # Subscribe this server
    server.subscribe()

    # Example for a 2nd server (same steps as above):
    # Remember to use a different port

    # server2             = cherrypy._cpserver.Server()

    # server2.socket_host = "0.0.0.0"
    # server2.socket_port = 8081
    # server2.thread_pool = 30
    # server2.subscribe()

    # Start the server engine (Option 1 *and* 2)

    cherrypy.engine.start()
    cherrypy.engine.block()
