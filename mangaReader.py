import requests
import os
import time
import re
import concurrent.futures
import img2pdf
from telegram.ext import *
from telegram import *
import patoolib
import bs4
import json
from Comic_Reader_v1 import *




def MangaImgs(base_link):
    headers ={

        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cookie': '__cfduid=d8494d9d2fc3fc4618cb70827bb99e9b51602172025; _ga=GA1.2.847719129.1602172026; _gid=GA1.2.895171302.1602172026; Hm_lvt_5ee99fa43d3e817978c158dfc8eb72ad=1602172028; __atssc=google%3B1; sid=977188625d4852fa80f9fa57ff5f0531479cbf9470d06eb8437530a71d4ce38e061dc8928bed7cf6; set=theme=0&h=0&img_load=5&img_zoom=2&img_tool=1&twin_m=0&twin_c=0&manga_a_warn=1&history=1&timezone=14; _gat_gtag_UA_17788005_10=1; Hm_lpvt_5ee99fa43d3e817978c158dfc8eb72ad=1602172294; __atuvc=9%7C41; __atuvs=5f7f347a06e1a3e5008',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58'

    }

    Solution = requests.get(base_link, headers=headers)
    Extracted = str(Solution.text)
    Index = Extracted.index('<div class="board">')
    Extracted = str(Extracted[Index:])
    LastIndex = Extracted.index('<div class="container content">')
    Solution = Extracted[:LastIndex]
    # print(Solution)
    data = json.loads(Solution[Solution.index('['): Solution.index(']') + 1])
    raw_links= [d['u'] for d in data]
    global raw_pages
    raw_pages = raw_links
    # print(raw_pages)
    # print(Extracted)
    return raw_pages


def download_manga(page_links,page_no):
    img_data = requests.get(page_links).content
    with open(f"{str(page_no)}.jpg", 'wb') as handler:
        handler.write(img_data)

def convert_manga(manga_name):
    global final_pages
    final_pages = []
    # comic_pages = os.listdir('.')
    for file in os.listdir("."):
        if file.endswith(".jpg"):
            final_pages.append(file)
    final_pages.sort(key=lambda f: int(re.sub('\D', '', f)))
    with open(f"{manga_name}.pdf", "wb") as f:
        f.write(img2pdf.convert([i for i in final_pages if i.endswith(".jpg")]))
    images = tuple(final_pages)
    patoolib.create_archive(f"{manga_name}.cbr",images,verbosity=-1)

def get_mangaName(base_link):
    headers = {

        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cookie': '__cfduid=d8494d9d2fc3fc4618cb70827bb99e9b51602172025; _ga=GA1.2.847719129.1602172026; _gid=GA1.2.895171302.1602172026; Hm_lvt_5ee99fa43d3e817978c158dfc8eb72ad=1602172028; __atssc=google%3B1; sid=977188625d4852fa80f9fa57ff5f0531479cbf9470d06eb8437530a71d4ce38e061dc8928bed7cf6; set=theme=0&h=0&img_load=5&img_zoom=2&img_tool=1&twin_m=0&twin_c=0&manga_a_warn=1&history=1&timezone=14; _gat_gtag_UA_17788005_10=1; Hm_lpvt_5ee99fa43d3e817978c158dfc8eb72ad=1602172294; __atuvc=9%7C41; __atuvs=5f7f347a06e1a3e5008',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58'

    }
    global manga_name
    Solution = requests.get(base_link, headers=headers)
    soup = bs4.BeautifulSoup(Solution.text, 'html.parser')
    manga_title = soup.title.text
    x = manga_title.split("-")
    manga_name =x[0].strip()
    b = list(manga_name)
    if ":" in b:
        lol = b.index(":")
        b.pop(lol)
        manga_name="".join(b)
        print(manga_name)
        return manga_name
    else:
        return manga_name

def delete_manga(fpdf,fcbr):
    for f in final_pages:
        os.remove(f)
    os.remove(fpdf)
    os.remove(fcbr)


def manga_root_manager(base_link,glag):
    try:
        print(">>Getting Manga name<<")
        global manga_name
        manga_name = get_mangaName(base_link)
        print(">>Getting Manga pages<<")
        raw_pages = MangaImgs(base_link)
        os.chdir("C:\\Users\\Shaun\\classroom\\pythonprojects\\ComicReader\\Imgs")
        global page_no
        page_no=1
        t1 = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for page_links in raw_pages:
                executor.submit(download_manga, page_links, page_no)
                page_no+=1
        t2 = time.perf_counter()
        print(f'>>Download complete in {round(t2 - t1,2)} seconds<<')
        print(">>Converting to PDF<<")
        convert_manga(str(manga_name))
        print(">>Task Complete<<")
        glag= True
        return glag
    except:
        glag=False
        return glag



