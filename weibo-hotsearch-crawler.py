import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import os

sys.setrecursionlimit(2000000000)

def crawl():

    my_options = webdriver.ChromeOptions()
    my_options.add_argument("headless")
    my_options.add_argument("--no-sandbox")

    ###Place chromedriver into a location within your PATH.
    ###Then put the directory of the chromedriver within the quotation marks below.
    chrome_driver = r''
    
    driver = webdriver.Chrome(executable_path=chrome_driver, options = my_options)
    driver.get('https://s.weibo.com/top/summary?Refer=top_hot&topnav=1&wvr=6')

    title_list = []
    number_list = []
    icon_list = []
    ranking_list = []

    global title_backup
    title_backup = title_list[:]
    global number_backup
    number_backup = number_list[:]
    global icon_backup
    icon_backup = icon_list[:]

    entry_elements = driver.find_elements_by_css_selector('tbody > tr')


    for entry_element in entry_elements:
        try:
            ranking_element = entry_element.find_element_by_css_selector('td[class = "td-01 ranktop"]')
            ranking_list.append(ranking_element.text)
        except:
            ranking_list.append("置顶")
            
        try:
            title_element = entry_element.find_element_by_css_selector('td > a[href]')
            title_list.append(title_element.text)
        except:
            title_list.append("No title")

        try:
            number_element = entry_element.find_element_by_css_selector('td > span')
            if number_element.text.isdigit():
                number_list.append(number_element.text)
            else:
                number_list.append('0')
        except:
            number_list.append('0')

        try:
            icon_element = entry_element.find_element_by_css_selector('td > i[class]')
            icon_list.append(icon_element.text)
        except:
            icon_list.append('')


    time_directory = 'HotSearchSnapshotData/' + time.ctime()
    for i in range(len(title_list)):
        

        if int(number_list[i]) == 0:
            if icon_list[i] == "商":
                time_entry = '·  '+ title_list[i] + ' ' + icon_list[i]
            elif i == 0:
                time_entry = '置顶  '+ title_list[i] + ' ' + icon_list[i]
            else:
                time_entry = '?  '+ title_list[i] + ' ' + icon_list[i]
                
        else:
            time_entry = ranking_list[i] + '  ' + title_list[i] + ' ' + str(number_list[i]) + '  '+ icon_list[i]

        try:
            time_file = open(time_directory,'a')
        except FileNotFoundError as e:
            os.makedirs("HotSearchSnapshotData")
            time_file = open(time_directory,'a')
        time_file.write(time_entry)
        time_file.write('\n')
        time_file.close()

        if show_all == 'y':
            print(entry)


    for topic in title_list:
   
        topic_directory = 'HotSearchTopicData/' + topic

        try:
            prev_file = open(topic_directory,'r')
        except FileNotFoundError as e:
            topic_entry = '#' + ranking_list[title_list.index(topic)] + ' ' + topic + ' ' + time.ctime() + ' 热度 ' + str(number_list[title_list.index(topic)])
            try:
                topic_file = open(topic_directory,'w')
            except FileNotFoundError as e:
                os.makedirs("HotSearchTopicData")
                topic_file = open(topic_directory,'w')
            topic_file.write(topic_entry)
            topic_file.write('\n')
            topic_file.close()

            title_backup = title_list[:]
            number_backup = number_list[:]
            icon_backup = icon_list[:]
            continue
        
        prev_file_text = str(prev_file.read())
        number_start = prev_file_text.rfind(' ')
        number_end = prev_file_text.find('\n',number_start,len(prev_file_text))
        prev_number = prev_file_text[number_start+1:number_end]

        ranking_start = prev_file_text.rfind('#')
        ranking_end = prev_file_text.find(' ',ranking_start,len(prev_file_text))
        
        prev_ranking = prev_file_text[ranking_start+1:ranking_end]
        
        ranking = ranking_list[title_list.index(topic)]
        number = int(number_list[title_list.index(topic)])
        

        if not ranking.isdigit() or not prev_ranking.isdigit():
            continue

        for this_topic in title_backup:
            if this_topic not in title_list:
                if title_backup.index(this_topic) < ranking_threshold:
                    print('#'+this_topic+' 掉下热搜榜，原排名 '+str(title_backup.index(this_topic)) + ' 原热度 ' +str(number_backup[number_backup.index(this_topic)]))

        if int(prev_number) == 0:
            continue
        if abs(int(ranking)-int(prev_ranking)) > ranking_sensitivity or abs(number-int(prev_number))/int(prev_number) > (sensitivity/100):
            delta = int(number) - int(prev_number)
            #print(delta)
            if delta > 0:
                print('#'+topic+' 热度上升 '+str(delta))
            if delta <= 0:
                print('#'+topic+' 热度下降 '+str(abs(delta)))
   
        topic_entry = '#' + ranking_list[title_list.index(topic)] + ' ' + topic + ' ' + time.ctime() + ' 热度 ' + str(number_list[title_list.index(topic)])
        topic_file = open(topic_directory,'a')
        topic_file.write(topic_entry)
        topic_file.write('\n')
        topic_file.close()

        title_backup = title_list[:]
        number_backup = number_list[:]
        icon_backup = icon_list[:]


def autocrawl():
    try:
        crawl()
        print('Data Acquired ' + time.ctime())
        time.sleep(t)
        autocrawl()
    except:
        print('Error. Restarting after 5s')
        time.sleep(5)
        autocrawl()


def manualcrawl():
    try:
        crawl()
        print('Data Acquired ' + time.ctime())
    except:
        print('Error')
        yesno = input('Show all results? [yes/no]')
        manualcrawl()
        print('Data Acquired ' + time.ctime())
        

default_sensitivity = 5
default_ranking_sensitivity = 5
default_ranking_threshold = 35

#Ask user to choose if they want to output alert in console
choice_alert = input('Alert mode? [y/n]')
if choice_alert == 'y':

    use_default = input('Use default alert parameters? [y/n]')
    if use_default == 'n':
        #Input and processing for hotness sensitivity
        sensitivity_input = input('Input hotness sensitivity in integer percentages\n')
        if sensitivity_input == '':
            sensitivity = default_sensitivity
        try:
            sensitivity = int(sensitivity_input)
        except:
            print("Invalid input. Default value for sensitivity will be used.\n")
            sensitivity = default_sensitivity

        #Input and processing for ranking sensitivity
        ranking_sensitivity_input = input('Input ranking sensitivity in threshold ranking change\n')
        if ranking_sensitivity_input == '':
            ranking_sensitivity = default_ranking_sensitivity
        try:
            ranking_sensitivity = int(ranking_sensitivity_input)
        except:
            print("Invalid input. Default value for ranking sensitivity will be used.\n")
            ranking_sensitivity = default_ranking_sensitivity

        #Input and processing for ranking threshold
        ranking_threshold_input = input('Input ranking threshold for falling off hotsearch\n')
        if ranking_threshold_input == '':
            ranking_threshold = default_ranking_threshold
        try:
            ranking_threshold = int(ranking_threshold_input)
        except:
            print("Invalid input. Default value for ranking threshold will be used.\n")
            ranking_threshold = default_ranking_threshold
    else:
        sensitivity = default_sensitivity
        ranking_sensitivity = default_ranking_sensitivity
        ranking_threshold = default_ranking_threshold
        
else:
    sensitivity = 10000
    ranking_sensitivity = 51
    ranking_threshold = -1


#Ask user to choose if they want to crawl just once or crawl repeatedly
once_or_repeat = input('Crawl once or crawl repeatedly? [o/r]')
if once_or_repeat == 'o':
    show_all = input('Show all results? [y/n]')
    crawl()
if once_or_repeat == 'r':
    show_all = 'n'
    t = int(input('Input crawling sleep period in integer seconds\n'))
    autocrawl()
