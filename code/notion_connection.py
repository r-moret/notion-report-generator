import requests
import datetime

class Connection():
    """Class to establish a connection with the database from the Notion's 
    Integration and perform actions or retrieves data from it.
    """

    def __init__(self, api_token: str, database_id: str) -> None:
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

        def report_content_from_id(self, report_id: str) -> str:
            # TODO:
            pass