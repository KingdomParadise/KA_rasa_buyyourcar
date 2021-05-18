from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from rasa_sdk.events import SlotSet

from datetime import datetime


class ActionValidatePhoneNumber(Action):
    def name(self) -> Text:
        return "action_validate-phone-number"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        valid_phone_number = False
        phone_number = ""

        entities = tracker.latest_message["entities"]

        phone_number_entities = [
            entity["value"] for entity in entities if entity["entity"] == "phone-number"
        ]

        ## TODO Define some rules/integrate with API to validate phone number
        if phone_number_entities:
            valid_phone_number = True
            phone_number = phone_number_entities[0]

        return [
            SlotSet("valid-phone-number", valid_phone_number),
            SlotSet("phone-number", phone_number),
        ]


class ActionValidateTime(Action):

    datatime_wrong_entries = 0

    def name(self) -> Text:
        return "action_validate-time-date"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        valid_date_time = False
        end_conversation = False

        time_start = ""
        time_end = ""
        date = ""

        entities = tracker.latest_message["entities"]

        time_date_entities = [
            entity["value"] for entity in entities if entity["entity"] == "time"
        ]

        if time_date_entities:

            value = time_date_entities[0]

            ## in case time given is interval (i.e --> saturday between 9 am till 11 am)
            if type(value) is dict:
                time_start = datetime.strptime(
                    value.get("from"), "%Y-%m-%dT%H:%M:%S.%f%z"
                ).time()

                time_end = datetime.strptime(
                    value.get("to"), "%Y-%m-%dT%H:%M:%S.%f%z"
                ).time()

                date = datetime.strptime(
                    value.get("from"), "%Y-%m-%dT%H:%M:%S.%f%z"
                ).date()

            ## other case is that value is a string
            else:
                time_start = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").time()
                date = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").date()

            ## validate time
            # get todays date
            today_date = datetime.today().date()
            # get current time
            curr_time = datetime.now().time()

            if date > today_date or (date == today_date and time_start > curr_time):
                valid_date_time = True
                date = date.strftime("%d-%m-%Y")
                time_start = str(time_start)
            else:
                self.datatime_wrong_entries += 1

        else:
            self.datatime_wrong_entries += 1

        if self.datatime_wrong_entries >= 2:
            end_conversation = True
            self.datatime_wrong_entries = 0

        time_start = ":".join(str(time_start).split(":")[:2])

        return [
            SlotSet("valid-date-time", valid_date_time),
            SlotSet("date", date),
            SlotSet("time", time_start),
            SlotSet("end-conversation", end_conversation),
        ]


class ActionEndStory(Action):
    def name(self) -> Text:
        return "action_end-story"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        payload = {"recipient_id": tracker.sender_id, "status": 301}

        dispatcher.utter_message(json_message=payload)
