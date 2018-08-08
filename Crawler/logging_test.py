import logging

log_path = '/home/auxesis/Documents/RIpple/Logs/log_test.log'

handlers = [logging.FileHandler(log_path), logging.StreamHandler()]

logging.basicConfig(filename=log_path,
                    format='%(asctime)s %(message)s',
                    filemode='w')
#Creating an object
logger=logging.getLogger()
#Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)
logger.handlers = handlers

#Test messages
logger.debug("Harmless debug Message")
logger.info("Just an information")
logger.warning("Its a Warning")
logger.error("Did you try to divide by zero")
logger.critical("Internet is down")