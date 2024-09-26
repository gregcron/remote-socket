import logging, colorlog, sys

stream_handler = logging.StreamHandler(stream=sys.stdout)

def setFormat(cformat="[%(asctime)s]-[%(thread)d] %(log_color)s%(message)s"):
	colors = {
		'DEBUG': 'cyan',
		'INFO': 'green',
		'WARNING': 'yellow',
		'ERROR': 'red',
		'CRITICAL': 'cyan'
	}
	formatter = colorlog.ColoredFormatter(cformat, log_colors=colors)
	stream_handler.setFormatter(formatter)


def Logger():
	logger = logging.getLogger("TicketMaster")
	logger.setLevel(logging.INFO)

	setFormat()

	logger.addHandler(stream_handler)

	return logging.getLogger("TicketMaster")