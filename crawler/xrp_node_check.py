import requests
import json
import datetime
import redis
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
from mailin import Mailin
import ConfigParser

# Init Parser
parser = ConfigParser.RawConfigParser()

# Email TODO - api key needs to be changed
mail_conf_path = r'/var/xrp_config/xrp_mailin.ini'
parser.read(mail_conf_path)
m = Mailin(parser.get('mailin', 'url'), parser.get('mailin', 'key'))

# Node Connection
xrp_node_conf_path = r'/var/xrp_config/xrp_node.ini'
parser.read(xrp_node_conf_path)
URL = parser.get('ripple_node', 'url')

# Redis Connection
xrp_redis_conf_path = r'/var/xrp_config/xrp_redis.ini'
parser.read(xrp_redis_conf_path)
pool = redis.ConnectionPool(host=parser.get('redis', 'host'), port=int(parser.get('redis', 'port')), db=int(parser.get('redis', 'db')))
r = redis.Redis(connection_pool=pool)

# Reference
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
logger = None

# TODO - Hardcoded
email_to = ['Jitender.Bhutani@auxesisgroup.com','bhutanijonu@gmail.com']
email_from = 'Jitender.Bhutani@auxesisgroup.com'


def init_logger():
    """
    Initialization of log object
    :return:
    """
    try:
        global logger
        log_path = '/var/log/xrp_logs/node_check_logs/node_%s.log' % (str(datetime.date.today()).replace('-', '_'))
        handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
        logging.basicConfig(filename=log_path, format='%(asctime)s %(message)s', filemode='a')
        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)
        logger.handlers = handlers
        return True
    except Exception as e:
        return False


def mail_body(state,updown):
    """
    Define mail body
    :param state:
    :param updown:
    :return:
    """
    body = 'Hi Team, <br><br>'
    body += 'Ripple server is now : <b>%s</b>'%(updown)
    body += '<br>State : ' + state
    body += '<br>Time : ' + str(datetime.datetime.now())
    body += '<br><br>Regards, '
    body += '<br> Auxesis Tech Team'
    return body


def send_email(email_from,email_to,body):
    """
    Sending email
    :param email_from:
    :param email_to:
    :param body:
    :return:
    """
    try:
        email_dict = {
                        "to": {email_to:email_to},
                        "from": [email_from],
                        "subject": "XRP Node Up/Down",
                        "html": body
                    }

        m.send_email(email_dict)
        return True
    except Exception as e:
        logger.error("Error send_email : " + str(e))
        return False


def check_node_sync():
    """
    RPC for getting server info
    :return:
    """
    try:
        payload['method'] = 'server_info'
        params = {}
        payload['params'] = [params]
        response = requests.post(URL, data=json.dumps(payload), headers=headers)
        json_res = json.loads(response.text)
        server_state = json_res.get('result',{}).get('info',{}).get('server_state','')
        return server_state == 'full',server_state
    except Exception as e:
        logger.error('Ripple Node is Down')
        logger.error("Error check_node_sync : " + str(e))
    return False,'Critical! Our Node is Down'


def send_notif_node_down(state):
    """
    Sending notification of server down
    :param state:
    :return:
    """
    try:
        logger.error('#' * 100)
        logger.error('Server is Down : ' + state + ' - ' + str(datetime.datetime.now()))
        logger.error('#' * 100)

        # Send Email
        for email_id in email_to:
            body = mail_body(state,updown='Down')
            send_email(email_from=email_from,email_to=email_id,body=body)
        return True
    except Exception as e:
        logger.error("Error send_notif_node_down : " + str(e))
        return False


def send_notif_node_up(state):
    """
    Sending notification of server up
    :param state:
    :return:
    """
    try:
        logger.error('#'*100)
        logger.error('Server is Up : ' + state + ' - ' + str(datetime.datetime.now()))
        logger.error('#' * 100)

        # Send Email
        for email_id in email_to:
            body = mail_body(state, updown='Up')
            send_email(email_from=email_from, email_to=email_id, body=body)
        return True
    except Exception as e:
        logger.error("Error send_notif_node_down : " + str(e))
        return False


def check_state(state,sync):
    try:
        if r.get('xrp_node_synced') == 'True':
            if not sync:
                send_notif_node_down(state)
                r.set('xrp_node_synced', False)
        else:
            if sync:
                send_notif_node_up(state)
                r.set('xrp_node_synced', True)
        logger.error('-' * 100)
        return True
    except Exception as e:
        logger.error("Error check_state : " + str(e))
        return False


def job_check_node():
    """
    Main Process
    :return:
    """
    try:
        init_logger()
        # Check
        logger.error('-'*100)
        logger.error(datetime.datetime.now())
        sync,state = check_node_sync()
        logger.error(state)
        logger.error(r.get('xrp_node_synced'))
        check_state(state,sync)
        return True
    except Exception as e:
        logger.error('Error job_check_node : ' + str(e))
        return False


def main():
    try:
        sched = BlockingScheduler(timezone='Asia/Kolkata')
        sched.add_job(job_check_node, 'interval', id='my_job_id', seconds=10)
        sched.start()
    except Exception as e:
        if logger:
            logger.error('Error main : ' + str(e))


if __name__ == "__main__":
    main()
