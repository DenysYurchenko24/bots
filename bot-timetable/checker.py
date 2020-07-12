import time

def is_new_timetable():
    import time
    import requests
    from bs4 import BeautifulSoup
    url = 'http://fitu.kubg.edu.ua/informatsiya/2016-11-14-12-46-05/rozklad-zanyat.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    k1 = soup.findAll(href='javascript:// Менеджмент')
    print('There are ' + str(len(k1)) + ' timetables at the moment')
    f1 = open('log.py')
    l = list(f1)
    print('Timetables number log: ' + str(l))
    print('The latest number of timetables: ' + str(l[len(l)-1]))
    f1.close()
    if int(len(k1)) == int(l[len(l)-1]):
        print('No new timetables' + '\n')
        print('Current check has been conducted at ' + time.strftime('%H:%M:%S'))
        b = [time.strftime('%H'), time.strftime('%M'), time.strftime('%S')]
        if int(b[0]) > 19:
            print('Next check will be conducted at 0' + str(int(b[0]) - 20) + ':' + str(b[1]) + ':' + str(b[2]) + '\n'*2)
        elif int(b[0]) < 6:
            print('Next check will be conducted at 0' + str(int(b[0]) + 4) + ':' + str(b[1]) + ':' + str(b[2]) + '\n'*2)
        else:
            print('Next check will be conducted at ' + str(int(b[0]) + 4) + ':' + str(b[1]) + ':' + str(b[2]) + '\n'*2)
    else:
        import smtplib
        HOST = "smtp.gmail.com"
        SUBJECT = "New timetable!"
        TO = "arbadacarba007@gmail.com"
        FROM = "python.notifies@gmail.com"
        text = "New timetable is on! You can download it here: http://fitu.kubg.edu.ua/informatsiya/2016-11-14-12-46-05/rozklad-zanyat.html"
        BODY = "\r\n".join((
            "From: %s" % FROM,
            "To: %s" % TO,
            "Subject: %s" % SUBJECT,
            "",
            text
        ))
        server = smtplib.SMTP(HOST)
        server.starttls()
        server.login('python.notifies@gmail.com', 't5I90-b4R!.')
        server.sendmail(FROM, [TO], BODY)
        server.quit()
        f2 = open('log.py', 'a')
        f2.write(str(len(k1)) + '\n')
        f2.close()
        print('Current check has been conducted at ' + time.strftime('%H:%M:%S'))
        b = [time.strftime('%H'), time.strftime('%M'), time.strftime('%S')]
        if int(b[0]) > 19:
            print('Next check will be conducted at 0' + str(int(b[0]) - 20) + ':' + str(b[1]) + ':' + str(b[2]) + '\n'*2)
        elif int(b[0]) < 6:
            print('Next check will be conducted at 0' + str(int(b[0]) + 4) + ':' + str(b[1]) + ':' + str(b[2]) + '\n'*2)
        else:
            print('Next check will be conducted at ' + str(int(b[0]) + 4) + ':' + str(b[1]) + ':' + str(b[2]) + '\n'*2)


import schedule

is_new_timetable()

def job():
    is_new_timetable()

schedule.every(5).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

