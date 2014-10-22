#
#   server.py
#
#   David Janes
#   2014-10-21
#
#   Listen for Mandrill mail connections
#   and save to a file

import json
import sys
import smtplib

import bottle
import bunch

class Server(object):
    def __init__(self, cfgd):
        self.cfgd = bunch.bunchify(cfgd)
        self._setup_delivery()

        self.deliver_otherwise = None
        self.deliver_emaild = {}

    def _setup_delivery(self):
        pass

    def run(self):
        bottle.route("/inbound", method="POST")(self.inbound)
        bottle.run(host=self.cfgd.inbound.host, port=self.cfgd.inbound.port)

    def inbound(self):
        """This receives the email from Mandrill"""

        bottle.response.content_type = "text/plain"

        mds_raw = bottle.request.forms.get('mandrill_events')
        if not mds_raw:
            bottle.response.status = 400

            return "400 Error: Expected 'mandrill_events'"

        mds = json.loads(mds_raw)
        for md in mds:
            self.routing(md["msg"])

        return "ok"

    def routing(self, msgd):
        """This routes the email to the proper address(es)"""

        msg_rcpt_email = msgd["email"]
        msg_from_email = msgd["from_email"]
        msg_raw = msgd["raw_msg"]

        ## find the message body
        nlnlx = msg_raw.find("\n\n")
        crnlcrnlx = msg_raw.find("\r\n\r\n")
        x = min(filter(lambda x: x != -1, [ nlnlx, crnlcrnlx, len(msg_raw), ]))
        msg_raw_body = msg_raw[x:]

        ## headers
        headers = []
        for tag, value in msgd["headers"].iteritems():
            tag = tag.lower()
            if tag.find("yahoo") > -1:
                continue
            elif tag.find("signature") > -1:
                continue

            if isinstance(value, list):
                headers.extend(value)
            else:
                headers.append(value)

        msg_raw_new = "\n".join(headers) + msg_raw_body

        if self.cfgd.routing.default:
            self.send(msg_from_email, [ self.cfgd.routing.default, ], msg_raw_new)

    def send(self, msg_from_email, msg_rcpts, msg_raw):
        """This sends the email to Mandrill for final delivery"""

        if self.cfgd.outbound.get('ssl', False):
            server = smtplib.SMTP_SSL(
                host=self.cfgd.outbound.host, 
                port=self.cfgd.outbound.port,
            )
        else:
            server = smtplib.SMTP(
                host=self.cfgd.outbound.host,
                port=self.cfgd.outbound.port,
            )

        server.set_debuglevel(1)

        server.login(self.cfgd.outbound.username, self.cfgd.outbound.password)
        server.sendmail(msg_from_email, msg_rcpts, msg_raw)
        server.quit()

if __name__ == '__main__':
    with open('server.json', 'r') as cin:
        cfgd = json.load(cin)

    server = Server(cfgd)
    server.run()
