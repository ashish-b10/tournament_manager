import logging
_log = logging.getLogger(__name__)

import httplib2
from urllib.parse import urlparse

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

import io
import odf.opendocument
import odf.table
import odf.text
import zipfile

SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

class GoogleDriveSpreadsheet():

    def __init__(self, downloader=None, file_id=None):
        self._downloader = downloader
        self.file_id = file_id
        if self._downloader is not None and self.file_id is not None:
            self._download_file()

    def spreadsheet_edit_url(self):
        """Returns the URL for editing a spreadsheet."""
        doc_key = self.file_id
        return "https://docs.google.com/spreadsheets/d/" + doc_key + "/edit"

    def _download_file(self):
        for i in range(5):
            response = self._downloader.download_file(self.file_id)
            try:
                self.load_doc(io.BytesIO(response))
                break
            except zipfile.BadZipFile:
                _log.exception("Received bad zip file downloading %s" %(
                        self.file_id))
                continue

    def load_doc(self, body):
        self.doc = odf.opendocument.load(body)
        self._parse_doc()

    def _parse_doc(self):
        self.sheets = {}
        tables = self.doc.spreadsheet.getElementsByType(odf.table.Table)
        for table in tables:
            table_name = table.getAttribute("name")
            self.sheets[table_name] = self._parse_table(table)

    def _parse_table(self, table):
        table_rows = table.getElementsByType(odf.table.TableRow)
        for table_row in table_rows:
            yield self._parse_table_row(table_row)

    def _parse_table_row(self, table_row):
        row = []
        for table_cell in table_row.getElementsByType(odf.table.TableCell):
            row+= self._parse_table_cell(table_cell)
        return row

    columns_repeated_qname = (
        'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'number-columns-repeated'
    )
    columns_spanned_qname = (
        'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'number-columns-spanned'
    )
    rows_repeated_qname = (
        'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'number-rows-repeated'
    )
    rows_spanned_qname = (
        'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
        'number-rows-spanned'
    )

    def _parse_table_cell(self, table_cell):
        cell_text = self._get_cell_text(table_cell)

        try:
            repeated_columns = int(
                    table_cell.attributes[self.columns_repeated_qname])
        except KeyError:
            repeated_columns = 1

        try:
            spanned_columns = int(
                    table_cell.attributes[self.columns_spanned_qname])
        except KeyError:
            spanned_columns = 0

        try:
            repeated_rows = int(
                    table_cell.attributes[self.rows_repeated_qname])
        except KeyError:
            repeated_rows = 0

        try:
            spanned_rows = int(
                    table_cell.attributes[self.rows_spanned_qname])
        except KeyError:
            spanned_rows = 1

        if repeated_rows != 0:
            raise NotImplementedError("Cell repeated %d rows" %repeated_rows)
        if spanned_rows != 1:
            _log.warn("Ignoring %s = %d" %(
                    self.rows_spanned_qname, spanned_rows))

        return [cell_text] * repeated_columns + [''] * spanned_columns

    def _get_cell_text(self, table_cell):
        child_nodes = table_cell.childNodes
        text_ps = list(filter(self._is_p_node, child_nodes))
        if not text_ps:
            return ''
        else:
            cell_text = []
            for text_p in text_ps:
                cell_text.append(self._parse_text_p(text_p))
        return ''.join(map(lambda x: x or '', cell_text))

    @staticmethod
    def _is_p_node(node):
        qname = node.qname
        return qname == ('urn:oasis:names:tc:opendocument:xmlns:text:1.0', 'p')

    def _parse_text_p(self, text_p):
        text = str(text_p)
        if not text:
            return None
        return text

if __name__ == "__main__":
    from .argparser import parser, init_logger
    args = parser.parse_args()
    credential_file = args.credential_file
    file_id = args.file_id
    verbose = args.verbose is None

    import sys
    init_logger(sys.stdout, verbose=True)

    from .gdocs_downloader import GoogleDocsDownloader
    downloader = GoogleDocsDownloader(credential_file)
    client = GoogleDriveSpreadsheet(downloader, file_id)

    for sheet_name,sheet in client.sheets.items():
        _log.info("Sheet [%s] has %d rows" %(sheet_name, len(list(sheet))))
