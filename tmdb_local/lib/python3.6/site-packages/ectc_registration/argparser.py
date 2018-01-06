__all__ = ["parser", "init_logger"]
import argparse
import logging
parser = argparse.ArgumentParser(prog="gdocs_downloader")
parser.add_argument('-c', '--credential-file', required=True,
        help='JSON-formatted file with Google account credentials')
parser.add_argument('-u', '--file-id', required=True,
        help='Identifier of the document to download (ie. ABCD1234 if downloading https://docs.google.com/spreadsheets/d/ABCD1234/edit)')
parser.add_argument('-v', '--verbose', required=False,
        help='Enable verbose (debug) logging')

def init_logger(stream, verbose=False):
    logging_format = '%(levelname)-5s %(name)s:%(lineno)4s - %(message)s'
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, stream=stream, format=logging_format)
