import xrp_node_check

xrp_node_synced = None

# def setup_module(module):
#     global xrp_node_synced
#     xrp_node_synced = xrp_node_check.r.get('xrp_node_synced')
#
# def teardown_module(module):
#     global xrp_node_synced
#     xrp_node_check.r.set('xrp_node_synced',xrp_node_synced)
#
#
# # Positive
# def test_init_logger():
#     assert xrp_node_check.init_logger() == True
#
# # Positive
# def test_mail_body():
#     state = 'test_state'
#     updown = 'test_updown'
#     assert bool(xrp_node_check.mail_body(state,updown)) == True
#
# # Positive
# def test_check_node_sync():
#     assert bool(xrp_node_check.check_node_sync()[1]) == True
#
# # Positive
# def test_job_check_node():
#     assert bool(xrp_node_check.job_check_node()) == True
#
# # Positive
# def test_check_statue_up():
#     state = 'test_state_up'
#     xrp_node_check.r.set('xrp_node_synced', False)
#     assert bool(xrp_node_check.check_state(state,sync = True)) == True
#
# def test_check_statue_down():
#     state = 'test_state_down'
#     xrp_node_check.r.set('xrp_node_synced', True)
#     assert bool(xrp_node_check.check_state(state,sync = False)) == True
#
# # Positive
# def test_send_notif_node_up():
#     state = 'Test_State_Up'
#     assert xrp_node_check.send_notif_node_up(state) == True
#
# # # Positive
# def test_send_notif_node_down():
#     state = 'Test_State_Down'
#     assert xrp_node_check.send_notif_node_down(state) == True
#
# # Positive
# def test_send_email():
#     email_from = 'Jitender.Bhutani@auxesisgroup.com'
#     email_to = 'Jitender.Bhutani@auxesisgroup.com'
#     body = 'Testing'
#     assert bool(xrp_node_check.send_email(email_from, email_to, body)) == True
#
# # Negative - Wrong Fields (email)
# def test_send_email_wrong_fields():
#     email_from = 'Jitender.Bhutani@auxesisgroup.com'
#     email_to = ['Jitender.Bhutani@auxesisgroup.com']
#     body = 'Testing'
#     assert bool(xrp_node_check.send_email(email_from, email_to, body)) == False