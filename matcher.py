import re
from dbWorker import dataBaseWorker


def prepareTask(line: str) -> [str]:
    line = line.lower()
    subject = re.search("(?<=добавь ).*(?= на \d{2}\.\d{2})",line)
    date = re.search("(?<=на )\d{2}\.\d{2}",line)
    description = re.search("(?<=\d{2}\.\d{2} ).*",line)
    return subject,date,description


def prepareAlias(line:str) -> [str]:
    line = line.lower()
    subject = re.search(".+(?= *,)",line).group()
    alias = re.search("(?<=,).+",line).group().strip()
    return [subject,alias]


def isAliasStringValid(line:str) -> bool:
    return re.fullmatch(".+,.+",line)!=None


def prepareSub(line:str) -> str:
    line = line.lower()
    subject = re.search("(?<=/newsub ).+",line).group()
    return subject


def isUserNameValid(line:str) -> bool:
    return re.fullmatch(r"[\w\d\-\_]{4,64}",line)!=None


def isPasswordValid(line:str)-> bool:
    return re.fullmatch(r".{8,1024}", line)!=None


def isDateValid(line:str)-> bool:
    return re.fullmatch(r"((0\d)|(1\d)|(2\d)|(3[01]))\.((0\d)|(1[012]))", line)!=None