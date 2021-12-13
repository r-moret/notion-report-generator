from notion_connection import Connection
from typing import Dict

import pandas as pd

import datetime


class ReportManager():
    """Manager class to access the handle the retrieving of reports from Notion's workspace.
    
    It gives a higher level of abstraction logically and in data responses than a direct
    connection with the Notion's database.

    Attributes
    ----------
    cxn : Connection
        Connection object to retrieve information from the Notion's Integration.
    author : str
        Name of the person who's the author of the reports in the Notion's workspace.
    """
    cxn = None
    author = None

    @classmethod
    def initialize(cls, author: str, api_token: str, database_id: str) -> None:
        """Initialize the class attributes of the class.

        Parameters
        ----------
        author : str
            Name of the person who's the author of the reports in the Notion's workspace.
        api_token : str
            API Token of the Notion's Integration you want to connect to.
        database_id : str
            TODO (To be deleted)
        """
        cls.cxn = Connection(api_token, database_id)
        cls.author = author

    @classmethod
    def obtain_report(cls, date: str) -> Dict:
        """Retrieves the relevant information and content of a report 
        given its date of creation.

        Parameters
        ----------
        date : str
            Date of creation of the report we are looking for.

        Returns
        -------
        Dict
            Returns a dictionary containing two elements, the general
            information of the report (Dict) and its content (List).

        Raises
        ------
        Exception
            Raises if the report is incomplete (any of the mandatory 
            attributes is not present).
        """
        report_info = cls.cxn.report_info_from_date(date)
        report_id = report_info["id"]
        report_props = report_info["properties"]

        # Mandatory attributes
        if not report_props["Día"]["date"]:
            raise Exception("ERROR: The report has no date.")
        elif not report_props["Horario"]["select"]:
            raise Exception("ERROR: The report has no shift selected.")

        # Optional attributes
        if not report_props["Comentarios importantes"]["rich_text"]:
            comments = ""
        else:
            comments = report_props["Comentarios importantes"]["rich_text"][0]["plain_text"]
        if not report_props["Compañeros"]["multi_select"]:
            colleagues = []
        else:
            colleagues = [col["name"] for col in report_props["Compañeros"]["multi_select"]]

        report_content = cls.cxn.report_content_from_id(report_id)
        visits, report_database = report_content.values()

        # TODO: And if there's no visit?
        visits = [visit["properties"]["Impresión"]["rich_text"][0]["plain_text"] for visit in visits]

        report_info = {
            "date": report_props["Día"]["date"]["start"],
            "shift": report_props["Horario"]["select"]["name"],
            "colleagues": colleagues,
            "comments": comments,
            "visits": visits,
        }

        def _filter_content(entry: Dict) -> Dict:
            props = entry["properties"]

            # Mandatory attributes
            if not props["Nombre"]["title"]:
                raise Exception("ERROR: Some entry has no name.")
            elif not props["Patio"]["select"]:
                raise Exception("ERROR: Some entry has no yard.")

            # Optional attributes
            if not props["Observaciones"]["rich_text"]:
                observations = ""
            else:
                observations = props["Observaciones"]["rich_text"][0]["plain_text"]
            if not props["Importante"]["rich_text"]:
                important = ""
            else:
                important = props["Importante"]["rich_text"][0]["plain_text"]
            if not props["Estado"]["select"]:
                state = ""
            else:
                state = props["Estado"]["select"]["name"]


            relevant = {
                "name": props["Nombre"]["title"][0]["plain_text"],
                "yard": props["Patio"]["select"]["name"],                
                "state": state,
                "observations": observations,
                "important": important,
            }

            return relevant

        report_database = [_filter_content(entry) for entry in report_database]

        return {"info": report_info, "content": report_database}


class Report():
    """Wrapper class of the reports stored in the Notion's workspace.
    """

    def __init__(self, date: str) -> None:
        """Asks for a certain date to the ReportManager in order to receive the
        report created on that date.

        Parameters
        ----------
        date : str
            Creation date of the report we are looking for.

        Raises
        ------
        Exception
            Raises if the ReportManager has not created a Connection before it
            is invoked to search for a report.
        """
        if not ReportManager.cxn:
            raise Exception("ERROR: The ReportManager has to be initialized first.")
        
        report = ReportManager.obtain_report(date)
        info, content = report.values()

        date = datetime.datetime.strptime(date, "%d/%m/%Y").strftime("%Y.%m.%d")

        self.date = date
        self.shift = info["shift"]
        self.participants = info["colleagues"] + [ReportManager.author]
        self.comments = info["comments"]
        self.visits = info["visits"]
        self.content = pd.DataFrame(content)

    def write(self) -> str:
        text = (
            f"{self.date} {', '.join(self.participants[:-1])} y {self.participants[-1]} ({self.shift.lower()})\n"
            f"\n"
            f"Hora de entrada:\n"
            f"Hora de salida:\n"
            f"\n"
            f"\n"
            f"Entradas:\n"
            f"Acogidas:    {(self.content['state'] == 'Acogida').sum()}\n"
            f"Bajas:       {(self.content['state'] == 'Baja').sum()}\n"
            f"Adopciones:  {(self.content['state'] == 'Adoptado').sum()}\n"
            f"\n"
            f"\n"
            f"Visitas:\n"
            f"\n"
            f"\n"
            f"Notas:\n"
            f"{self.comments}\n"
            f"\n"
            f"\n"
        )
        return text
        
    def __str__(self) -> str:
        report = f"({self.date} - {self.shift}: {self.participants})"
        return report