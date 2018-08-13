import requests
import json
import datetime
import redis
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from mailin import Mailin

# TODO - api key needs to be changed
m = Mailin("https://api.sendinblue.com/v2.0", "vHmXBYOLTaMIyENj")
URL = 'http://167.99.228.1:5005'
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)

LOG_PATH = '/var/log/xrp_logs/node_check_logs/node_%s.log'%(str(datetime.date.today()).replace('-','_'))
handlers = [logging.FileHandler(LOG_PATH), logging.StreamHandler()]
logging.basicConfig(filename=LOG_PATH,format='%(asctime)s %(message)s',filemode='a')
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.handlers = handlers

# TODO - Harcoded
email_to = ['Jitender.Bhutani@auxesisgroup.com','bhutanijonu@gmail.com']
email_from = 'Jitender.Bhutani@auxesisgroup.com'

def mail_body(state,updown):
    body = 'Hi Team, <br><br>'
    body += 'Ripple server is now : <b>%s</b>'%(updown)
    body += '<br>State : ' + state
    return body

def send_email(email_from,email_to,body):
    try:
        email_dict = {
                        "to": {email_to:email_to},
                        "from": [email_from],
                        "subject": "Node Up/Down",
                        "html": body
                    }

        m.send_email(email_dict)
    except Exception as e:
        logging.error("Error send_email : " + str(e))

def check_node_sync():
    try:
        payload['method'] = 'server_info'
        params = {}
        payload['params'] = [params]
        response = requests.post(URL, data=json.dumps(payload), headers=headers)
        json_res = json.loads(response.text)
        server_state = json_res.get('result',{}).get('info',{}).get('server_state','')
        return server_state == 'full',server_state
    except Exception as e:
        logging.error('Ripple Node is Down')
        logging.error("Error check_node_sync : " + str(e))
    return False,''


def send_notif_node_down(state):
    try:
        logging.error('#' * 100)
        logging.error('Node Not Syncing : ' + state + ' - ' + str(datetime.datetime.now()))
        logging.error('#' * 100)

        # Send Email
        for email_id in email_to:
            if not state:
                state = 'Critical! Our Node is Down'
            body = mail_body(state,updown='Down')
            send_email(email_from=email_from,email_to=email_id,body=body)

    except Exception as e:
        logging.error("Error send_notif_node_down : " + str(e))


def send_notif_node_up(state):
    try:
        logging.error('#'*100)
        logging.error('Server is Up : ' + state + ' - ' + str(datetime.datetime.now()))
        logging.error('#' * 100)

        # Send Email
        for email_id in email_to:
            body = mail_body(state, updown='Up')
            send_email(email_from=email_from, email_to=email_id, body=body)

    except Exception as e:
        logging.error("Error send_notif_node_down : " + str(e))


def job_check_node():
    try:
        logging.error('-'*100)
        logging.error(datetime.datetime.now())
        sync,state = check_node_sync()
        logging.error(state)
        logging.error(r.get('xrp_node_synced'))
        if r.get('xrp_node_synced') == 'True':
            if not sync:
                send_notif_node_down(state)
                r.set('xrp_node_synced', False)
        else:
            if sync:
                send_notif_node_up(state)
                r.set('xrp_node_synced', True)
        logging.error('-' * 100)
    except Exception as e:
        logging.error('Error job_check_node : ' + str(e))


def main():
    try:
        sched = BlockingScheduler(timezone='Asia/Kolkata')
        sched.add_job(job_check_node, 'interval', id='my_job_id', seconds=10)
        sched.start()
    except Exception as e:
        logging.error('Error main : ' + str(e))

if __name__ == "__main__":
    main()
