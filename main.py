#!/usr/bin/env python3
from typing import NoReturn
import requests
import re
from yt_dlp import YoutubeDL
from threading import Thread

def _download_video(url : str):
    with YoutubeDL({"quiet": True}) as ydl: ydl.download(url)

def download_video(url):
    Thread(target=_download_video, args=[url]).start()

def no_match_found(url: str, regex: str) -> NoReturn:
    raise Exception(f"no match found\nurl: {url}\nregex: {regex}")

def search_in_response(url : str, regex : str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
    r = requests.get(url=url, headers=headers)
    res = re.search(regex, r.text)
    return res.group(1) if res != None else no_match_found(url, regex)

def tg1():
    regex = r'(http:\/\/mediapolisvod\.rai\.it\/relinker\/relinkerServlet\.htm\?cont=[a-zA-Z0-9]+)'
    url = search_in_response("https://www.rainews.it/notiziari/tg1", regex) + "&output=61"

    # https://stackoverflow.com/questions/35673914/indexerror-no-such-group-python
    url = search_in_response(url,  r'<!\[CDATA\[(.*)]]>')
    download_video(url)

def tgla7():
    url = "https://tg.la7.it/ultime-edizioni-del-tgla7"
    regex = r'(repliche-tgla7\?id=[0-9]+)"'
    latest_video = "https://tg.la7.it/" + search_in_response(url, regex)

    latest_video = search_in_response(latest_video, r'mp4: \"(.*\.mp4)"')    
    download_video(latest_video)

def corriere(url : str, regex: str):
    latest_video = search_in_response(url, regex)
    if (input(f"download {latest_video}?: ").lower() == "y"):
        video_id = search_in_response(latest_video, r'privateId\": \"([a-zA-Z0-9\-]+)\"')
        download_video("https://www.dailymotion.com/video/" + video_id)
   
def televideo(pg_num):
    url = f"https://www.televideo.rai.it/televideo/pub/catturaSottopagine.jsp?pagina={pg_num}&regione="
    # https://stackoverflow.com/questions/8303488/regex-to-match-any-character-including-new-lines
    # tautology not-space or space
    regex = r"<!-- SOLOTESTO PAGINA E SOTTOPAGINA -->([\S\s]*)<!-- \/SOLOTESTO PAGINA E SOTTOPAGINA -->" 
    solotesto= search_in_response(url, regex)

    garbage_regexs = [r"<.*?>", # html tag non-greedy regex (match as first as possible)
                                # https://stackoverflow.com/questions/11301387/python-regex-first-shortest-match
    r"&nbsp;", r"www\.servizitelevideo\.rai\.it.*", "RAI INFORMA a pagina [0-9]*"]
    for r in garbage_regexs:
        solotesto = re.sub(pattern = r, repl = "", string = solotesto).strip()
    
    print("EMPTY") if len(solotesto) == 0 else print(solotesto)

url = "https://video.corriere.it/esteri/oriente-occidente/"
regex = r'"(https:\/\/video\.corriere\.it\/esteri\/oriente-occidente\/.+\/[a-z0-9\-]+)"\n'
corriere(url=url, regex=regex)

url = "https://video.corriere.it/cronaca/fotosintesi-beppe-severgnini/"
regex = r'"(https:\/\/video\.corriere\.it\/cronaca\/fotosintesi-beppe-severgnini\/.+\/[a-z0-9\-]+)"\n'
corriere(url=url, regex=regex)

url = "https://video.corriere.it/cronaca/palomar-antonio-polito/"
regex = r'"(https:\/\/video\.corriere\.it\/cronaca\/palomar-antonio-polito\/.+\/[a-z0-9\-]+)"\n'
corriere(url=url, regex=regex)

if (input("download tg1?: ").lower() == "y"): tg1()
if (input("download tgla7?: ").lower() == "y"): tgla7()

while True:
    televideo(input())
