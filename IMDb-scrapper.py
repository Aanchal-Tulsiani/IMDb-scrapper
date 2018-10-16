import imdb
import urllib
from bs4 import BeautifulSoup
from imdb import IMDb
from datetime import datetime
from datetime import date
import pymysql
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def mysql(email, series):
    db = pymysql.connect("localhost","root","password","mysql")

    cursor = db.cursor()

    sql1 = "Create database [IF NOT EXISTS] IMDbDatabase"
       
    try:
       cursor.execute(sql1)
       db.commit()
    except:
       db.rollback()

    sql4 = "use IMDbDatabase"
       
    try:
       cursor.execute(sql4)
       db.commit()
    except:
       db.rollback()
       
    sql2 = "create table [IF NOT EXISTS] record(email varchar(100), series varchar(720))"
       
    try:
       cursor.execute(sql2)
       db.commit()
    except:
       db.rollback()

    sql3 = "INSERT INTO record VALUES ('%s', '%s' )" % (email, series)
       
    try:
       cursor.execute(sql3)
       db.commit()
    except:
       db.rollback()

    db.close()


def send_mail(email, content):
    email_user="tester@gmail.com"
    email_send=email
    subject="Schedule of your favourite TV series"
    password="password"

    msg=MIMEMultipart()
    msg['From']=email_user
    msg['To']=email_send
    msg['Subject']=subject

    msg.attach(MIMEText(content,'plain'))
    text=msg.as_string()
    server=smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,password)

    server.sendmail(email_user,email_send,text)
    server.quit()


def scrap(series):
    ia=IMDb()
    data=series.split(",")
    content="" 
    string1="Tv series name:"
    status="Status:"
    for movie in data:
        series_name=ia.search_movie(movie)[0]
        url=str(ia.get_imdbURL(series_name))
        initial_url="https://www.imdb.com"

        page=urllib.request.urlopen(url)
        soup = BeautifulSoup(page,"lxml")
        
        if(soup.find('div',attrs={'class':'seasons-and-year-nav'})==None):
            print("Please spell the series name correctly for :"+movie)
            continue
        next_url=soup.find('div',attrs={'class':'seasons-and-year-nav'}).find('a').get('href')
        n_url=initial_url+str(next_url)
        page2=urllib.request.urlopen(n_url)
        soup=BeautifulSoup(page2, 'lxml')

        present=datetime.now().date()
        str2=""
        strn=soup.find('div',attrs={'class':'airdate'}).contents[0]

        if(len(strn.strip())<2):
            str2="There is currently no imformation about upcoming episodes"

        else:		
            air_date = strn.strip()
            str3=air_date.split(" ")
            if(len(str3)==1):
                c_data=str3.pop()
                if present.year<=int(c_data):
                    str2="The next season will begin in " + c_data
                else:
                    str2="The show has finished streaming all its episodes"					
            else:	
                m=0
                risk=soup.find_all('div',attrs={'class':'airdate'})
                for j in risk:
                    k=j.contents[0]
                    if(len(k.strip())<2):
                            str2="There is currently no imformation about upcoming episodes"
                            break
                    k=k.strip()
                    a,b,c=k.split(' ')
                    var={"Jan.":1, "Feb.":2, "Mar.":3, "Apr.":4, "May.":5, "Jun.":6, "Jul.":7, "Aug.":8, "Sep.":9, "Oct.":10, "Nov.":11, "Dec.":12, "Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
                    str4=var[b]
                    date_string = c+"-"+str(str4)+"-"+a
                    now = date(*map(int, date_string.split('-')))
                    if(now>=present and m==0):
                        str2="The next season begins on "+date_string
                        break
                    else:
                        if(now>=present):
                            str2="The next episode will air on "+date_string
                            break 
                        m=m+1
                if(m==len(risk)):
                    str2="The show has finished streaming all its episodes"
        content=content+string1+movie+"\n"+status+str2+"\n\n"
    return content


while(1):
    email=input("Enter email address: ")
    series=input("Enter series separated by commas: ")

    mysql(email, series)
    content=scrap(series)
    send_mail(email,content)
