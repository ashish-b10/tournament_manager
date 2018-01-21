import logging
_log = logging.getLogger(__name__)

from .gdocs_downloader import GoogleDocsDownloader
from .gdrive_spreadsheet import GoogleDriveSpreadsheet

class RegistrationExtractor():
    def __init__(self, workbook):
        self._workbook = workbook

    def get_registration_workbooks(self):
        """Gets the registration workbooks in the registration document.

        Returns:
            A list of schools and their registration document URLs.
        """
        school_rows = self._workbook.sheets['Schools']
        next(school_rows) # school registrations start in row 3
        next(school_rows)
        registered_schools = []
        for row in school_rows:
            if row[0] == "TOTALS:":
                break #end of schools list
            school_name = row[0]
            doc_url = row[2]

            if not doc_url.startswith("http"):
                continue #no registration document provided

            try:
                approved = row[4]
            except IndexError:
                approved = ''

            registered_schools.append(SchoolRegistrationExtractor(
                    school_name=school_name, registration_doc_url=doc_url,
                    approved=(approved == "Yes")))

        return registered_schools

class SchoolRegistrationExtractor():

    TEAM_SHEET_NAMES = ["Mens_A", "Mens_B", "Mens_C", "Womens_A", "Womens_B",
            "Womens_C"]

    def __init__(self, school_name, registration_doc_url, approved=False):
        self.school_name = school_name
        self.registration_doc_url = registration_doc_url
        self.approved = approved

    def extract(self, doc_downloader):
        doc_url = self.registration_doc_url
        file_id = GoogleDocsDownloader.extract_file_id(doc_url)
        _log.debug("Importing %s from %s", self.school_name, file_id)
        workbook = GoogleDriveSpreadsheet(doc_downloader, file_id)
        self.extract_competitors(workbook)
        self.extract_teams(workbook)

    def extract_competitors(self, workbook):
        roster = workbook.sheets['Weigh-Ins']
        for i in range(10):
            next(roster) #roster starts on 11th row

        self.extracted_competitors=[]
        for row in roster:
            if not row[3]:
                #_log.debug("Skipping empty line")
                continue
            competitor = {}
            competitor['name'] = row[3]
            competitor['rank'] = row[4]
            competitor['sex'] = row[6]
            if not row[20]:
                _log.debug(competitor['name'] + " has empty weight field")
                self.extracted_competitors.append(competitor)
                continue
            try:
                competitor['weight'] = float(row[20])
            except ValueError:
                _log.warning("Failed to parse weight field [%s] for %s" %(
                        row[20], competitor['name']))
            self.extracted_competitors.append(competitor)

    def extract_teams(self, workbook):
        self.teams = {}
        for sheet_name in self.TEAM_SHEET_NAMES:
            teams = self.extract_division_teams(workbook.sheets[sheet_name])
            self.teams[sheet_name] = teams

    def download_division_teams_csv(self, sheet_url, doc_downloader):
        division_teams_body = doc_downloader.download_file(sheet_url)[1]
        return doc_downloader.body_to_csv(division_teams_body)

    def extract_division_teams(self, team_sheet):
        for i in range(6):
            next(team_sheet) # teams start on 7th line

        return [self.read_team(team_sheet) for i in range(10)]

    def read_team(self, division_teams_rows):
        # read lightweight, middleweight, heavyweight, alternate1, alternate2
        members = [next(division_teams_rows)[3] for i in range(5)]
        return members if any(members) else None

def log_teams(school):
    for team_sheet_name in SchoolRegistrationExtractor.TEAM_SHEET_NAMES:
        for team_num, team_roster in enumerate(school.teams[team_sheet_name]):
            if not team_roster:
                continue

            _log.info("Recorded %s %d: %s" %(team_sheet_name, team_num+1,
                    str(team_roster)))

if __name__ == "__main__":
    from .argparser import parser, init_logger
    args = parser.parse_args()
    credential_file = args.credential_file
    file_id = args.file_id
    verbose = args.verbose is None

    import sys
    init_logger(sys.stdout, verbose=verbose)

    downloader = GoogleDocsDownloader(credential_file)
    master_workbook = GoogleDriveSpreadsheet(downloader, file_id)
    reg_extracter = RegistrationExtractor(master_workbook)
    registered_schools = reg_extracter.get_registration_workbooks()
    _log.info("Parsed %d registered schools" %(len(registered_schools)))

    for school in registered_schools:
        _log.info("Importing for %s from %s"
                %(school.school_name, school.registration_doc_url))
        school.extract(downloader)
        _log.info("Parsed %d competitors from %s"
                %(len(school.extracted_competitors), school.school_name))

        log_teams(school)
