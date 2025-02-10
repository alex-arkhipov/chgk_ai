import re
import logging

logger = logging.getLogger(name=__name__)

class ChgkQuestion:

    def __init__(self, question: str, answer:str) -> None:
        question = question
        self.question = question
        # Remove trialing dots
        if (answer[-1] == '.'):
            answer = answer[:-1]
        self.answer = answer


    def hasPicture(q: "ChgkQuestion") -> bool:
        try:
            pics = re.findall(pattern=r'^\(pic: \d+\.[\w\d]+\)', string=q.question)
            if len(pics)>0:
                return True
        except Exception as e:
            logger.error(msg=f'findall error ({e}: {q.question}')
        return False
