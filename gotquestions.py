import datetime
import logging
from os import listdir, path, mkdir
from bs4 import BeautifulSoup
import json

import chgk_question
import chgk_data

PACK_PATH = 'gotquestions/'
HTML_EXT = '.html'
QUESTIONS_EXT = '.dat'
LOG_DIR = 'logs/'


logger = logging.getLogger(name=__name__)

def setupLogger(logDir=LOG_DIR) -> None:
    if not path.exists(path=logDir):
        mkdir(path=logDir)

    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s: %(module)s: %(levelname)s: %(message)s',
                        filename=f'{logDir}gotq_{datetime.datetime.now().strftime(format="%Y-%m-%d_%H-%M")}.log',
                        level=logging.INFO)


def getHTMLFullFileName(pack) -> str:
    chgkData = chgk_data.ChgkData.getInstance(type=chgk_data.CHGK_TYPE_GOTQUESTIONS)
    return chgkData.getPackPath(pack=pack) + str(object=pack) + HTML_EXT


def getNextPack():
    for dir_name in listdir(path=PACK_PATH):
        yield dir_name


def getHTML(pack):
    fileName = getHTMLFullFileName(pack=pack)
    if not path.exists(path=fileName):
        return None
    with open(file=fileName, mode='r') as f:
        return f.read()


def getQuestions(pack):
    html = getHTML(pack=pack)
    if html is None:
        logger.error(msg=f"HTML for pack {pack} not found")
        return None
    # Парсим HTML при помощи Beautiful Soup
    soup = BeautifulSoup(markup=html, features='html.parser')

    script = soup.find(name='script', attrs={'id': '__NEXT_DATA__'})
    try:
        data = json.loads(s=script.text)
        data2 = data['props']['pageProps']['pack']['tours']
    except Exception as e:
        logger.error(msg=f"Pack {pack}: Cannot parse: {e}")
        data2 = data['props']['pageProps']
        if data2.get('tour') is None:
            logger.error(msg=f"Pack {pack}: No tours found")
            return None
        data2 = [data2['tour']]
    questions = []
    for tour in data2:
        for question in tour['questions']:
            id = question.get('id')
            if id is None:
                logger.error(msg=f"Pack {pack}: Question has no id. Skip this question.")
                continue
            text = question.get('text')
            if text is None:
                logger.error(msg=f"Pack {pack}: Question {id} has no text. Skip this question.")
                continue
            answer = question.get('answer')
            if answer is None:
                logger.error(msg=f"Pack {pack}: Question {id} has no answer. Skip this question.")
                continue
            razdatka = question.get('razdatkaPic')
            if razdatka:
                logger.info(msg=f"Pack {pack}: Question {id} has razdatka. Skip this question.")
                continue
            try:
                q = chgk_question.ChgkQuestion(question=text, answer=answer)
            except Exception as e:
                logger.error(msg=f"Pack {pack}: Question {id}: Text {text}: Answer {answer}: Error ({e}). Skip this question.")
                continue
            questions.append(q)
    return questions


def main() -> None:
    setupLogger()
    count = 0
    chgkData = chgk_data.ChgkData.getInstance(type=chgk_data.CHGK_TYPE_GOTQUESTIONS)
    for pack in getNextPack():
        if chgkData.isQuestionsExist(pack=pack):
            logger.debug(msg=f"Skipping pack {pack}: already has questions")
            continue
        questions = getQuestions(pack=pack)
        if questions is None:
            logger.error(msg=f"Pack {pack}: Cannot get questions")
            continue
        chgkData.saveData(tournament_id=pack, questions=questions, force=True)
        logger.info(msg=f"Pack {pack}: Got {len(questions)} questions")
        count += len(questions)
    logger.info(msg=f"Total {count} questions")


if __name__ == "__main__":
    main()
