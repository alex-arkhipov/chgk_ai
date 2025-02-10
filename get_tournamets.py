# Get all tournaments from site and save them to file

import datetime
from os import mkdir, path
import logging

import chgk_xml
import chgk_data

logger = logging.getLogger(name=__name__)

def setupLogger(logDir) -> None:
    if not path.exists(path=logDir):
        mkdir(path=logDir)

    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s: %(module)s: %(levelname)s: %(message)s',
                        filename=logDir + datetime.datetime.now().strftime(format="%Y-%m-%d_%H-%M") + ".log",
                        level=logging.INFO)

def main() -> None:
    setupLogger(logDir='log/')
    chgkData = chgk_data.ChgkData.getInstance(type=chgk_data.CHGK_TYPE_INFO)
    # Get all tournaments from XML

    #chgk_ai_utils.check_all_tournaments()
    return

    data = chgk_xml.get_final_tournaments(tournament_id='0', limit=0) # Many tournaments
    # Check if there is only one tournament
    if (type(data) is not list):
        data = [data]
    
    for tour in data:
        id = tour['id']
        questions = tour['questions']
        if (not questions):
            # Save tournaments to file
            chgkData.saveData(tournament_id=id, questions=questions)

    print('Done!')


if __name__ == "__main__":
    main()
