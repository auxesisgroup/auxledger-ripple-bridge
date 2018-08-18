import xrp_node_check
import datetime

xrp_node_synced = None
log_path = '/var/log/xrp_logs/node_check_logs/node_%s.log' % (str(datetime.date.today()).replace('-', '_'))

def test_init_logger():
    assert xrp_node_check.init_logger() == True

def setup_module(module):
    global xrp_node_synced
    xrp_node_synced = xrp_node_check.r.get('xrp_node_synced')

def teardown_module(module):
    global xrp_node_synced
    xrp_node_check.r.set('xrp_node_synced',xrp_node_synced)

# ++++++ Init Logger
def test_init_logger():
    assert xrp_node_check.init_logger(log_path) == True

# ------ Init Logger - Wrong Path
def test_init_logger_wrong_path():
    log_path = '/wrong_path/'
    assert xrp_node_check.init_logger(log_path) == False

# ++++++ Mail Body
def test_mail_body():
    state = 'test_state'
    updown = 'test_updown'
    assert bool(xrp_node_check.mail_body(state,updown)) == True

# ++++++ Check Node Sync
def test_check_node_sync():
    assert bool(xrp_node_check.check_node_sync()[1]) == True

# ------ Check Node Sync - Wrong URL
def test_check_node_sync_wrong_url():
    correct_url = xrp_node_check.URL
    xrp_node_check.URL = 'wrong_url'
    res = xrp_node_check.check_node_sync()[0]
    xrp_node_check.URL = correct_url
    assert res == False

# ++++++ Send Email
def test_send_email():
    email_from = 'Jitender.Bhutani@auxesisgroup.com'
    email_to = 'Jitender.Bhutani@auxesisgroup.com'
    body = 'Testing'
    assert bool(xrp_node_check.send_email(email_from, email_to, body)) == True

# ------ Send Email - Wrong Fields (email)
def test_send_email_wrong_fields():
    email_from = 'Jitender.Bhutani@auxesisgroup.com'
    email_to = ['Jitender.Bhutani@auxesisgroup.com']
    body = 'Testing'
    assert bool(xrp_node_check.send_email(email_from, email_to, body)) == False

# ++++++ Send Node Down Notification
def test_send_notif_node_down():
    state = 'Test_State_Down'
    assert xrp_node_check.send_notif_node_down(state) == True

# ++++++++ Send Node Up Notification
def test_send_notif_node_up():
    state = 'Test_State_Up'
    assert xrp_node_check.send_notif_node_up(state) == True

# ++++++ Check State Up
def test_check_state_up():
    state = 'test_state_up'
    xrp_node_check.r.set('xrp_node_synced', False)
    assert bool(xrp_node_check.check_state(state,sync = True)) == True

# ++++++ Check State Down
def test_check_state_down():
    state = 'test_state_down'
    xrp_node_check.r.set('xrp_node_synced', True)
    assert bool(xrp_node_check.check_state(state,sync = False)) == True

# ++++++ Job Check Node
def test_job_check_node():
    assert bool(xrp_node_check.job_check_node()) == True