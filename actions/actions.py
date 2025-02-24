# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import re
from rasa_sdk import Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.interfaces import Tracker
from typing import Text, Dict, Any, List

import logging

logger = logging.getLogger(__name__)


class ActionCheckCandidate(Action):
    def name(self) -> Text:
        return "action_check_candidate"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # получаем значения из слотов
        position = tracker.get_slot("position")
        experience = int(tracker.get_slot("experience"))
        skills = tracker.get_slot("skills")
        salary = tracker.get_slot("salary")

        if not all([position, experience, skills, salary]):
            dispatcher.utter_message(text="Пожалуйста, заполните все обязательные поля.")
            return []

        # Преобразуем строку навыков в список, если это строка
        if isinstance(skills, str):
            skills = [skill.strip() for skill in skills.split(",")]  # Преобразуем строку в список

        # Заданные требования для разных ролей
        required_experience = {
            "Data Scientist": 2,
            "Project Manager": 3,
            "Data Engineer": 2,
            "Data Analyst": 1,
            "MLOps Engineer": 2
        }

        required_skills = {
            "Data Scientist": ["Python", "ML"],
            "Project Manager": ["Agile", "Scrum"],
            "Data Engineer": ["SQL", "ETL"],
            "Data Analyst": ["SQL", "BI"],
            "MLOps Engineer": ["Docker", "Kubernetes"]
        }

        # Проверка на соответствие требованиям
        if position in required_experience:
            min_exp = required_experience[position]
            if experience >= min_exp and any(skill in skills for skill in required_skills[position]):
                dispatcher.utter_message(text="Отлично, ты подходишь на эту вакансию! Передаю твои данные рекрутеру.")
            else:
                dispatcher.utter_message(text="К сожалению, ты не соответствуешь требованиям.")
        else:
            dispatcher.utter_message(text="Эта роль у нас пока не открыта.")

        return []


