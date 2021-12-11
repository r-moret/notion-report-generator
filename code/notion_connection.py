import requests
import datetime

from typing import Dict, List


class Connection():
    """Class to establish a connection with the database from the Notion's 
    Integration and perform actions or retrieves data from it.
    """

    def __init__(self, api_token: str, database_id: str) -> None:
        # TODO: The database_id is not needed, it can be obtain directly
        # with a search in the Integration, decoupling the Connection from
        # the database and linking it directly and exclusively with the API
        """Initializer of the class. Saves the necessary data to establish
        the connection with the Notion's database.

        Parameters
        ----------
        api_token : str
            API Token of the Notion's Integration.
        database_id : str
            ID of the database from the workspace that you would 
            like to connect to.
        """
        self.API_TOKEN = api_token
        self.DATABASE_ID = database_id
        self.DEF_HEADER = {
            "Notion-Version": "2021-08-16",
            "Authorization": "Bearer " + self.API_TOKEN,
        }
    

    def report_info_from_date(self, report_date: str) -> str:
        """Retrieves the report information from the report created on the 
        specified day. Returns the information on JSON format.

        Parameters
        ----------
        report_date : str
            Date when the report was written.

        Returns
        -------
        str
            JSON string containing all the information of the report.

        Raises
        ------
        Exception
            Wether exists none or too many reports in the same date.
        """
        url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"

        headers = {key: value for key, value in self.DEF_HEADER.items()}
        headers["Content-Type"] = "application/json"

        report_date = datetime.datetime.strptime(report_date, "%d/%m/%Y")
        report_date = report_date.strftime("%Y-%m-%d")

        query = {
            "filter": {
                "property": "Día",
                "created_time": {
                    "equals": report_date
                }
            }
        }

        reports = requests.post(url, headers=headers, json=query).json()["results"]

        if len(reports) == 0:
            raise Exception("ERROR: There is no report written on that date.")
        elif len(reports) > 1:
            raise Exception("ERROR: More than one report within the same date.")
        
        report = reports[0]
        return report


    def report_content_from_id(self, report_id: str) -> List[Dict]:
        """Retrieves the content of the inner database from a specified report.

        Parameters
        ----------
        report_id : str
            Report ID whose content we want to obtain.

        Returns
        -------
        List[Dict]
            List of entries in the inner database. Each entry is
            a dictionary.

        Raises
        ------
        Exception
            Raises if the report contains none or more than one inner databases.
        """
        url_report = f'https://api.notion.com/v1/blocks/{report_id}/children'

        report_blocks = requests.get(url_report, headers=self.DEF_HEADER).json()["results"]
        inner_dbs = [block["id"] for block in report_blocks if block["type"] == "child_database"]

        if len(inner_dbs) != 1:
            raise Exception(f"ERROR: Something went wrong with the format on page {report_id}")

        database_id = inner_dbs[0]

        url_database = f"https://api.notion.com/v1/databases/{database_id}/query"

        headers = {key: value for key, value in self.DEF_HEADER.items()}
        headers["Content-Type"] = "application/json"

        query = {}

        response = requests.post(url_database, headers=headers, json=query).json()
        results = response["results"]

        while response["has_more"]:
            query = {
                "start_cursor": response["next_cursor"],
            }

            response = requests.post(url_database, headers=headers, json=query).json()
            results = results + response["results"]

        return results
