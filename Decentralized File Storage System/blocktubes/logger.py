import logging
block_logger = logging.getLogger("block_logger")

# uncomment the lines below to save logs to a file
# logfile = 'tube.log'
# file_handler = logging.FileHandler(logfile)
# block_logger.addHandler(file_handler)

# this one-liner might work, too
block_logger.addHandler(logging.FileHandler('tube.log'))
