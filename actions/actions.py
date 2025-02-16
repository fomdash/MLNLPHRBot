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
       # Получаем значения из слотов
       role = tracker.get_slot("role")
       experience = tracker.get_slot("experience")
       skills = tracker.get_slot("skills")
       logger.debug(f"Текущие навыки: {skills}")
       salary_expectation = tracker.get_slot("salary_expectation")

       # Проверка на обязательные поля
       if not all([role, experience, skills, salary_expectation]):
           dispatcher.utter_message(text="Пожалуйста, заполните все обязательные поля.")
           return [SlotSet("action_completed", False)]

       # Преобразуем опыт в целое число, извлекая только цифры
       experience = self.extract_experience(experience)

       # Преобразуем строку навыков в список, если это строка
       if isinstance(skills, str):
           skills = [skill.strip() for skill in skills.split(",")]  # Убираем пробелы  # Преобразуем строку в список

       # Извлекаем зарплату
       salary = self.extract_salary(salary_expectation)
       if salary is None:
           dispatcher.utter_message(
               text="Не удалось извлечь ожидаемую зарплату. Пожалуйста, введите корректное значение.")
           return [SlotSet("action_completed", False)]

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
       if role in required_experience:
           min_exp = required_experience[role]
           if experience >= min_exp and any(skill in skills for skill in required_skills[role]):
               dispatcher.utter_message(text="Отлично, ты подходишь на эту вакансию! Передаю твои данные рекрутеру.")
           else:
               dispatcher.utter_message(text="К сожалению, ты не соответствуешь требованиям.")
       else:
           dispatcher.utter_message(text="Эта роль у нас пока не открыта.")

       return [SlotSet("action_completed", True)]

   def extract_experience(self, experience: str) -> int:
       # Регулярное выражение для извлечения числового значения опыта
       match = re.search(r'\d+', experience)
       if match:
           # Возвращаем извлечённое число
           return int(match.group(0))
       return 0  # Если не нашли числа, возвращаем 0

   def extract_salary(self, salary_expectation: str) -> float:
       # Извлекаем только цифры из строки зарплаты
       if salary_expectation:
           salary_expectation = salary_expectation.replace(" ", "")  # Убираем пробелы
           match = re.search(r"\d+", salary_expectation)  # Ищем числа
           if match:
               return float(match.group(0))
       return None


class ActionProvideRole(Action):
    def name(self):
        return "action_provide_role"

    def run(self, dispatcher, tracker, domain):
        role = tracker.get_slot("role")
        dispatcher.utter_message(text=f"Ты выбрал роль {role}. Теперь давай поговорим о твоих зарплатных ожиданиях.")
        return [SlotSet("role", role)]