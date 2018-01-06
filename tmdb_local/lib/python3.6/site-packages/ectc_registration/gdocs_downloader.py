import logging
_log = logging.getLogger(__name__)

import httplib2
from urllib.parse import urlparse

import json

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

class GoogleDocsDownloader():

    ODS_MIME_TYPE = 'application/x-vnd.oasis.opendocument.spreadsheet'

    def __init__(self, creds_file=None, creds_json=None, download=True):
        if creds_file:
            _log.info("Loading credentials from %s" %creds_file)
        self.drive_service = self._create_drive_service(creds_file, creds_json)

    @staticmethod
    def extract_file_id(doc_url):
        return urlparse(doc_url).path.split('/')[3]

    @staticmethod
    def _create_drive_service(creds_file=None, creds_json=None):
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

        if creds_json is not None:
            creds = json.loads(creds_json)
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds, SCOPES)
        elif creds_file is not None:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    creds_file, SCOPES)
        else:
            raise ValueError("Either creds_file or creds_json must be defined")
        http_auth = credentials.authorize(httplib2.Http())

        return build('drive', 'v3', http=http_auth)

    def download_file(self, file_id):
        """Downloads a file using the Drive service."""
        _log.info("Attempting to download %s" %(file_id))
        request = self.drive_service.files().export(
                fileId=file_id, mimeType=self.ODS_MIME_TYPE)

        num_attempts = 5
        for i in range(num_attempts):
            try:
                response = request.execute()
            except Exception as e:
                _log.exception("Failed to request %s" %(file_id))
                continue
            return response
        raise IOError("Exhausted %d attempts to download %s" %(
                num_attempts, file_id))

if __name__ == "__main__":
    from .argparser import parser
    args = parser.parse_args()
    credential_file = args.credential_file
    file_id = args.file_id
    verbose = args.verbose is None

    import sys
    logging_format = '%(levelname)-5s %(name)s:%(lineno)4s - %(message)s'
    if verbose:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                format=logging_format)
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                format=logging_format)

    client = GoogleDocsDownloader(credential_file)

    response = client.download_file(file_id)
    _log.info("Received %d bytes from %s" %(len(response), file_id))
