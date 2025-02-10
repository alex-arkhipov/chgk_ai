# Utility file for chgk ai project

import os
import logging

import chgk_question
import chgk_data
import chgk_xml

logger = logging.getLogger(name=__name__)

TOURNAMETS_FILE = "tournaments.dat" # All tournaments IDs
LAST_HANDLED_TOURNAMENT_FILE = "last_handled_tournament.dat" # Last handled tournament ID
CHGK_DIR = "chgk"


# Get all tournaments from XML
def get_all_tournaments():

    pass


def save_all_tournaments():
    pass


def check_all_tournaments() -> None:
    logger.info(msg="Checking tournaments")
    chgkData = chgk_data.ChgkData.getInstance()
    count = 0
    for dir_name in os.listdir(path=chgkData.dir):
        if not chgkData.hasQuestions(tournament_id=dir_name):
            q = chgk_xml.get_inner_tournaments(tournament_id=dir_name)
            if len(q) == 1 and q[0].get('questions'):
                questions = q[0].get('questions')
                questions = remove_picture_questions(questions=questions)
                if len(questions) > 0:
                    logger.info(msg=f"Found {len(questions)} questions for tournament {dir_name}")
                    chgkData.saveData(tournament_id=dir_name, questions=questions, force=True)
                    count += 1
    logger.info(msg=f"Saved {count} tournaments with questions")


def remove_picture_questions(questions):
    ret = []
    if not questions:
        return ret
    for question in questions:
        if not chgk_question.ChgkQuestion.hasPicture(q=question):
            ret.append(question)
    return ret
