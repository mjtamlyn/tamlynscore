from urllib.parse import quote


class DomainRedirect(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ.get('HTTP_HOST'):
            host = environ['HTTP_HOST']
        else:
            host = environ['SERVER_NAME']

        canonical_host = environ.get('CANONICAL_HOST', 'www.tamlynscore.co.uk')
        if host == canonical_host:
            return self.app(environ, start_response)

        url = 'https://'
        url += canonical_host
        url += quote(environ.get('SCRIPT_NAME', ''))
        url += quote(environ.get('PATH_INFO', ''))
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']

        status = "301 Moved Permanently"
        headers = [('Location', url),('Content-Length', '0')]

        start_response(status, headers)

        return ['']
