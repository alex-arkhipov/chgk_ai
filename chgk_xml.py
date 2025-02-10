# Utils to work with XML data from dbchgk.info site

import requests
from requests.exceptions import RequestException
import xmltodict
import logging

import chgk_data
import chgk_question
import chgk_ai_utils

logger = logging.getLogger(name=__name__)

URL_TOURNAMETS = "https://db.chgk.info/tour/xml/"

URL_BASE = "https://db.chgk.info/tour/"
URL_ENDING = "xml/"


def get_all_tournaments_url() -> str:
    return f'{URL_BASE}{URL_ENDING}'


def get_tournament_url(tournament_id: str) -> str:
    return f'{URL_BASE}{tournament_id}/{URL_ENDING}'


def get_tournament(tournament_id: str):
    logger.info(msg=f"Getting tournament {tournament_id}")
    try:
        url = get_tournament_url(tournament_id=tournament_id)
        r = requests.get(url=url)
    except RequestException as e:
        logger.error(msg=f"Error during HHTP request: {e}")
        return None
    try:
        data = xmltodict.parse(xml_input=r.content)
    except Exception as e:
        logger.error(msg=f"Error during xmlparsing: {e}\n{r.content}")
        return None
    q = data.get('tournament')
    if (not q):
        logger.error(msg=f'Cannot parse URL response: {data}')
        return None
    return q


def get_inner_tournaments(tournament_id: str):
    logger.info(msg=f"Getting inner tournaments for {tournament_id}")
    tours = []
    q = get_tournament(tournament_id=tournament_id)
    if (not q):
        logger.error(msg=f'Cannot get tournament {tournament_id}')
        return tours
    if (not q.get('tour')):
        # Try to get questions
        questions = get_questions(tournament=q)
        if (not questions): # No questions
            logger.error(msg=f'Cannot get neither inner tournament not questions for {tournament_id}')
            return tours
        ret = {}
        ret['id'] = tournament_id
        ret['questions'] = questions
        tours.append(ret)
    else:
        # Inner tournaments
        tours_tmp = q.get('tour')
        if (type(tours_tmp) is not list):
            tours_tmp = [tours_tmp]
        for tour in tours_tmp:
            id = tour.get('Id')
            ret = {}
            ret['id'] = id
            ret['questions'] = None
            tours.append(ret)
    return tours

def get_questions(tournament):
    logger.info(msg=f"Getting questions for {tournament.get('Id')}")
    ret = []
    questions = tournament.get('question')
    if (not questions):
        logger.error(msg=f"Cannot get questions for {tournament}")
        return []
    if (type(questions) is not list):
        questions = [questions]

    for question in questions:
        try:
            ret.append(chgk_question.ChgkQuestion(question=question.get('Question'), answer=question.get('Answer')))
        except Exception as e:
            logger.error(msg=f"Error during parsing question: {e}")
            logger.error(msg=f"Question: {question}")
    logger.info(msg=f"Got {len(ret)} questions for {tournament.get('Id')}")
    return ret

def get_all_tournaments():
    logger.info(msg="Getting all tournaments")
    data = get_inner_tournaments(tournament_id=0)
    if (not data):
        logger.error(msg="Cannot get all tournaments")
        return None
    return data

def get_final_tournaments(tournament_id: str, limit = 0):
    logger.info(msg=f"Getting final tournaments (tour_id={tournament_id})")
    tours = []
    chgkData = chgk_data.ChgkData.getInstance()
    if (chgkData.isTournamentExists(tournament_id=tournament_id)):
        logger.info(msg=f"Tournament {tournament_id} is already in database")
        return tours

    data = get_inner_tournaments(tournament_id=tournament_id)
    if (len(data) == 0):
        logger.error(msg=f"Cannot get final tournaments (tour_id={tournament_id})")
    if (len(data) == 1 and data[0]['questions'] is not None):
        # It is final tournament
        tours.append(data[0])
        questions = data[0]['questions']
        questions = chgk_ai_utils.remove_picture_questions(questions=questions)
        chgkData.saveData(tournament_id=tournament_id, questions=questions)
    else:
        tmp = {}
        tmp['id'] = tournament_id
        tmp['questions'] = None
        tours.append(tmp) # add empty ones as well
        for tour in data:
            inner_tour = get_final_tournaments(tournament_id=tour['id'])
            tours.extend(inner_tour)
            if (limit > 0 and len(tours) > limit):
                break
    return tours
