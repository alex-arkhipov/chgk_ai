import requests
import logging
import datetime
from os import mkdir, path

BASE_URL = 'https://gotquestions.online/pack/'
MAX_PACK = 2500

PATH_TO_SAVE = 'gotquestions/'
EXT = '.html'
FILE_404 = '404'
LOG_DIR = 'logs/'


logger = logging.getLogger(name=__name__)

def setupLogger(logDir=LOG_DIR) -> None:
    if not path.exists(path=logDir):
        mkdir(path=logDir)

    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s: %(module)s: %(levelname)s: %(message)s',
                        filename=f'{logDir}scrap_{datetime.datetime.now().strftime(format="%Y-%m-%d_%H-%M")}.log',
                        level=logging.INFO)


def getHTMLPath(pack) -> str:
    return f'{PATH_TO_SAVE}{pack}/'


def getHTMLFullFileName(pack) -> str:
    return getHTMLPath(pack=pack) + str(object=pack) + EXT


def getUrl(pack) -> str:
    return BASE_URL + str(object=pack)


def getHTML(pack) -> str:
    url = getUrl(pack=pack)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    response = requests.get(url=url, headers=headers)
    if (response.status_code != 200):
        logger.error(msg=f"Error {response.status_code} while getting HTML from {url}")
        return None
    return response.text


def make404File(pack) -> None:
    dir = getHTMLPath(pack=pack)
    if not path.exists(path=dir):
        mkdir(path=dir)
    x = dir + FILE_404
    open(file=x, mode='w').close()


def is404File(pack) -> bool:
    return path.exists(path=getHTMLPath(pack=pack) + FILE_404)


def saveHTML(pack, html) -> None:
    htmlPath = getHTMLPath(pack=pack)
    if not path.exists(path=htmlPath):
        mkdir(path=htmlPath)
    with open(file=getHTMLFullFileName(pack=pack), mode='w', encoding='utf-8') as f:
        f.write(html)


def isHTMLExists(pack) -> bool:
    return path.exists(path=getHTMLFullFileName(pack=pack))


def main() -> None:
    setupLogger()
    count = 0
    for i in range(1, MAX_PACK + 1):
        if isHTMLExists(pack=i):
            logger.debug(msg=f"HTML for pack {i} already exists")
            continue
        if is404File(pack=i):
            logger.info(msg=f"HTML for pack {i} is 404")
            continue
        html = getHTML(pack=i)
        if html is None:
            logger.error(msg=f"HTML for pack {i} not found!")
            make404File(pack=i)
            continue
        saveHTML(pack=i, html=html)
        logger.info(msg=f"HTML for pack {i} saved")
        count += 1
    logger.info(msg=f"Total {count} HTMLs saved")


if __name__ == "__main__":
    main()
