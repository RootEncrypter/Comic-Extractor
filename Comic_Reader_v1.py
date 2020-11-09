import requests
import os
import time
import re
import concurrent.futures
import threading
import img2pdf
from telegram.ext import *
from telegram import *
import patoolib
from mangaReader import *
from telegram.ext.dispatcher import run_async


# -----------------------------------------------Comic Module--------------------------------------------------

def comicImgs(base_link):
    headers ={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cookie': '__cfduid=d270ded5dba31bfa204ef6db14ae5c5961602050741; rhid_c=0; _ga=GA1.2.2118227203.1602050746; _gid=GA1.2.1644230706.1602050746; _gat=1; RHDIPOPrhpmin=yes; RHDIPOPrhpmax=1%7CThu%2C%2008%20Oct%202020%2006%3A05%3A47%20GMT; _gat_gtag_UA_128776493_23=1; fpestid=rsNuou1xKymuIey8_nrjjDhQSbtyPIJKeBlb8au4KiyOrRErbq0Aa2ZAm4DfPC7HOArGmA; rco_readType=1; rco_quality=hq; AdskeeperStorage=%7B%220%22%3A%7B%7D%2C%22C880361%22%3A%7B%22page%22%3A4%2C%22time%22%3A1602050788766%7D%7D',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58'

    }

    Solution = requests.get(base_link, headers=headers)
    # time.sleep(2)
    Extracted = str(Solution.text)
    Index = Extracted.index('var lstImages = new Array();')
    Extracted = str(Extracted[Index:])
    LastIndex = Extracted.index('var currImage = 0;')
    Solution = Extracted[:LastIndex]
    raw_links = re.findall(r'https?:\/\/\S*', str(Solution))
    global raw_pages
    raw_pages = ' '.join(raw_links).replace('");','').split()
    # print(raw_pages)
    return raw_pages



def download_comics(page_links,page_no):
    img_data = requests.get(page_links).content
    with open(f"{str(page_no)}.jpg", 'wb') as handler:
        handler.write(img_data)

def convert_comic(comic_name):
    global comic_pages
    comic_pages= []
    # comic_pages = os.listdir('.')
    for file in os.listdir("."):
        if file.endswith(".jpg"):
            comic_pages.append(file)
    comic_pages.sort(key=lambda f: int(re.sub('\D', '', f)))
    with open(f"{comic_name}.pdf", "wb") as f:
        f.write(img2pdf.convert([i for i in comic_pages if i.endswith(".jpg")]))
    # images = tuple(comic_pages)
    # patoolib.create_archive(f"{comic_name}.cbr",images,verbosity=-1)





def get_comicName(base_link):
    x = base_link.split("/")
    cname1= x[4]
    y = x[5].split("?")
    cname2 = y[0]
    comic_name=f"{cname1}-{cname2}"
    return comic_name


def delete_comic():
    for f in comic_pages:
        os.remove(f)
    os.remove(fpdf)
    # os.remove(fcbr)


def comic_root_manager(r_obj):
    try:
        update = r_obj['user']
        base_link = r_obj['url']
        print(">>Getting Comic name<<")
        global comic_name
        comic_name= get_comicName(base_link)
        print(">>Getting Comic pages<<")
        raw_pages= comicImgs(base_link)
        os.chdir("C:\\Users\\Shaun\\classroom\\pythonprojects\\ComicReader\\Imgs")
        global page_no
        page_no=1
        t1 = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for page_links in raw_pages:
                executor.submit(download_comics, page_links, page_no)
                page_no+=1
        t2 = time.perf_counter()
        print(f'>>Download complete in {round(t2 - t1,2)} seconds<<')
        print(">>Converting to PDF<<")
        convert_comic(comic_name)
        print(">>Task Complete<<")
        global fpdf
        global fcbr
        fpdf = ("{0}.pdf".format(comic_name))
        # fcbr = ("{0}.cbr".format(comic_name))
        print(">>Uploading...<<")
        update.message.reply_document(document=open(fpdf, 'rb'),timeout=1000)
        print(">>Upload Complete<<")
        print("----------------------------------------------")
        delete_comic()
        os.chdir("C:\\Users\\Shaun\\classroom\\pythonprojects\\ComicReader")
    except Exception as e:
        print(e)
        
        


global my_list
my_list =[]

def process_queue():
    while True:
        if my_list:
            comic_root_manager(my_list[0])
            my_list.pop(0)
        else:
            time.sleep(1)




# --------------------------------------------Telegram Module-------------------------------------------------
def message(update, context):
    try:
        if update.message.text.startswith('!comic'):
            try:
                print(">>Preparing for User: " + update.message.chat.username)
            except :
                print(">>Preparing for User: " + update.message.chat.first_name)
            update.message.reply_text("`Request in Queue`",parse_mode ='Markdown')
            got_data = re.findall(r'https?:\/\/\S*', update.message.text)
            global base_link
            base_link = got_data[0]
            global request_object
            request_object = {'user':update,'url': base_link}
            my_list.append(request_object)
        elif update.message.text.startswith('!manga'):
            print(">>Preparing for User: " + update.message.chat.username)
            update.message.reply_text("`Request in Queue`",parse_mode ='Markdown')
            got_data = re.findall(r'https?:\/\/\S*', update.message.text)
            base_link = got_data[0]
            global glag
            glag = True
            lag=manga_root_manager(base_link,glag)
            if lag == True:
                manga_name = get_mangaName(base_link)
                # global fpdf
                # global fcbr
                fpdf = ("{0}.pdf".format(manga_name))
                fcbr = ("{0}.cbr".format(manga_name))
                # print(fpdf)
                print(">>Uploading...<<")
                update.message.reply_document(document=open(fpdf, 'rb'), timeout=1000)
                # update.message.reply_document(document=open(fcbr, 'rb'), timeout=1000)
                print(">>Upload Complete<<")
                print("----------------------------------------------")
                delete_manga(fpdf,fcbr)
                os.chdir("C:\\Users\\Shaun\\classroom\\pythonprojects\\ComicReader")
            else:
                update.message.reply_text("`Invalid Request.`", parse_mode='Markdown')
        else:
            update.message.reply_text("`Invalid Format , Try Again!!`",parse_mode ='Markdown')
    except:
        update.message.reply_text("`Invalid Request.`", parse_mode='Markdown')



def start(update, context):
    base_message = f"""
{'```'}

[*]【How To Use】[*]

[*]To Download Comic :-
[*]Type !comic <YOUR COMIC LINK>

[*]To Download Manga :-
[*]Type !manga <YOUR MANGA LINK>

[*]【Working Sites】[*]
[*] readcomiconline.to (!comic)[*]
[*] mangapark.com (!manga) [*]

[*]【Notes】[*]
[*] Avoid Single Page Links [*]
[*] make Sure Link has All Pages [*]

[$]--Comic World--[$]

{'```'}
"""
    update.message.reply_text(base_message,parse_mode ='Markdown')


def main():
    updater =Updater(TOKEN,use_context=True)
    dp =updater.dispatcher
    dp.add_handler(CommandHandler("start",start))
    # user_handler =MessageHandler(Filters.chat(username=config['usernames']),restricted_user_space)
    # dp.add_handler(user_handler)
    dp.add_handler(MessageHandler(Filters.text, message))
    updater.start_polling()
    # updater.idle()


p1 = threading.Thread(target=main)
p2 = threading.Thread(target=process_queue)

if __name__ == '__main__':
    
    global base_path
    # base_path =os.getcwd()
    # print(base_path)
    os.chdir("C:\\Users\\Shaun\\classroom\\pythonprojects\\ComicReader")
    print(">>Proceeding to Comic Hub<<")
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    



    

    
