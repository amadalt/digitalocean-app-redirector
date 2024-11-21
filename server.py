#!/usr/bin/python3

import os
import flask
import requests
import urllib.parse

teamserver          = os.environ.get('TEAMSERVER', '185.208.158.155')

rewrite_host_header = True

method_requests_mapping = {
    'GET': requests.get,
    'HEAD': requests.head,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete,
    'PATCH': requests.patch,
    'OPTIONS': requests.options,
}

def create_app():
    app = flask.Flask(__name__)

    @app.route('/', defaults={'path': ''}, methods=method_requests_mapping.keys())
    @app.route('/<path:path>', methods=method_requests_mapping.keys())
    def main(path):

        url     = flask.request.url
        headers = dict(flask.request.headers)
        params  = flask.request.args
        method  = flask.request.method
        body    = flask.request.data

        try:
            print(f'[proxy] Request: {method} "{url}"')
            parsed  = urllib.parse.urlparse(url)
            url = parsed._replace(netloc = teamserver).geturl()
            print(f'[proxy] Replaced URL to: "{url}"')

            if rewrite_host_header:
                prevHost = headers['Host']
                headers['Host'] = teamserver
                print(f'[proxy] Altered Host from: {prevHost} to: {teamserver}')

            requests_function = method_requests_mapping[method.upper()]

            request = flask.request.base_url
            
            print('[proxy] Issuing reverse-proxy request...')
            request = requests_function(url, headers=headers, stream=True, params=flask.request.args)

            response = flask.Response(
                flask.stream_with_context(request.iter_content()),
                content_type = request.headers['content-type'],
                status = request.status_code
            )

            print('[proxy] Got response.')
            return response

        except Exception as e:
            print(f'[proxy] Exception thrown: "{e}"')
            pass

        print('[proxy] Finished main() with empty result.')
        return ""

    return app
