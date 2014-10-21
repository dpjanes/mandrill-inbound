#
#   server.py
#
#   David Janes
#   2014-10-21
#
#   Listen for Mandrill mail connections
#   and save to a file

import bottle
import json
import sys

cfgd = {
    "host": '0.0.0.0',
    "port": 9090,
}

@bottle.route('/inbound', method='POST')
def inbound_POST():
    bottle.response.content_type = "text/plain"

    mds = request.forms.get('mandrill_events')
    if not mds:
        bottle.response.status = 400

        return "400 Error: Expected 'mandrill_events'"

    print(sys.stderr, json.dumps(mds, sort_keys=True, indent=2))
    return "ok"

@bottle.route('/inbound')
def inbound():
    bottle.response.content_type = "text/plain"
    bottle.response.status = 405

    return "405 Error: Try again with POST"

bottle.run(host=cfgd['host'], port=cfgd['port'])
