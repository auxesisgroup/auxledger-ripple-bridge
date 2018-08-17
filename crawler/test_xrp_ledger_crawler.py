import xrp_ledger_crawler

def test_init_logger():
    assert xrp_ledger_crawler.init_logger() == True