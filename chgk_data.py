import os
import pickle
import logging

logger = logging.getLogger(name=__name__)

TOURNAMETS_FILE = "tournaments.dat" # All tournaments IDs

CHGK_TYOE = ''
CHGK_TYPE_INFO = 'db.chgk.info'
CHGK_TYPE_GOTQUESTIONS = 'gotquestions'

CHGK_DIRS = {CHGK_TYPE_INFO: "chgk", CHGK_TYPE_GOTQUESTIONS: 'gotquestions'}
QUESTIONS_FILE = "questions.dat"


class ChgkData:
    __instance = None


    def getInstance(type) -> "ChgkData":
        if (not ChgkData.__instance):
            ChgkData(type=type)
        return ChgkData.__instance


    def __init__(self, type) -> None:
        self.qtype = type
        if (type == CHGK_TYPE_INFO):
            self.dir = CHGK_DIRS[CHGK_TYPE_INFO]
        elif (type == CHGK_TYPE_GOTQUESTIONS):
            self.dir = CHGK_DIRS[CHGK_TYPE_GOTQUESTIONS]
        else:
            raise ValueError(f"Unknown type: {type}")
        self.data = {}
        self.__loadData(dir=self.dir)
        ChgkData.__instance = self
        logger.info(msg=f"ChgkData ({self.qtype}) initialized")


    def __loadData(self, dir) -> None:
        logger.info(msg="Loading data")
        counter = 0
        empty_counter = 0
        questions_count = 0
        if not os.path.exists(path=dir):
            logger.info(msg="Creating tournament directory")
            os.mkdir(path=dir)
        else:
            for dir_name in os.listdir(path=self.dir):
                file_path = f'{self.dir}/{dir_name}/{QUESTIONS_FILE}'
                if os.path.exists(path=file_path):
                    with open(file=file_path, mode='rb') as f:
                        self.data[dir_name] = ChgkData.__decodeData(data=f.read())
                    counter += 1
                    questions_count += len(self.data[dir_name])
                else:
                    self.data[dir_name] = None
                    empty_counter += 1
        logger.info(msg=f"Loaded {counter} tournaments (questions: {questions_count}) and {empty_counter} empty tournaments")


    def getTournamentQuestions(self, tournament_id: str) -> list:
        return self.data.get(tournament_id)


    def getPackPath(self, pack) -> str:
        return f'{self.dir}/{pack}/'


    def getQuestionsFullFileName(self, pack) -> str:
        return self.getPackPath(pack=pack) + QUESTIONS_FILE


    def isQuestionsExist(self, pack) -> bool:
        return os.path.exists(path=self.getQuestionsFullFileName(pack=pack))


    def isTournamentExists(self, tournament_id: str) -> bool:
        try:
            self.data[tournament_id]
        except KeyError:
            return False
        return True


    def hasQuestions(self, tournament_id: str) -> bool:
        return self.data.get(tournament_id) is not None


    def saveData(self, tournament_id, questions, force=False) -> None:
        path = self.getPackPath(pack=tournament_id)
        exists = os.path.exists(path=path) 
        if exists and not force:
            logger.warning(msg=f"Tournament {tournament_id} already exists")
            return
        if not exists:
            os.mkdir(path=path)
        empty = ' empty '
        if questions:
            encoded_data = ChgkData.__encodeData(data=questions)
            file_name = self.getQuestionsFullFileName(pack=tournament_id)
            with open(file=file_name, mode='wb') as f:
                f.write(encoded_data)
            empty = ' '
        self.data[tournament_id] = questions
        logger.info(msg=f"Saved{empty}tournament {tournament_id}")


    def __decodeData(data):
        data = pickle.loads(data)
        return data


    def __encodeData(data) -> bytes:
        return pickle.dumps(obj=data)
