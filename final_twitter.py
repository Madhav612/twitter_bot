import pandas as pd
import numpy as np
import tweepy as tw
import json,requests
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
import datetime
import re
import time
from urllib.request import urlopen
from textblob import TextBlob
import os

from selenium import webdriver #web scraping
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys#Input of keys
from selenium.common.exceptions import NoSuchElementException
import pychrome#chrome developer tools neeeded to simulate geolocation
from contextlib import closing
import socket 
from urllib.request import urlopen
import emoji
consumer_key = 'XXXXXXXXXXXXXXXXXXXXXX' #Enter your key 
consumer_secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
access_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
access_token_secret='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)
model = T5ForConditionalGeneration.from_pretrained('t5-small')
tokenizer = T5Tokenizer.from_pretrained('t5-small')
def is_connected():#To check the internet conncetion
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except:
        return False
def loop_connected():#This function is called to check the internet connection thruoghout the code which will call is_connected() 
    if is_connected(): #If internet connection is there, it will return True and remaining code will continue
        return True
    else:#If false, it will wait 10 seconds for internet connection and try again
        print("Internet Disabled")
        time.sleep(10)
        loop_connected()#Call itself again
        
def find_free_port():#Use to find free ports on localhost
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
def give_emoji_free_text(text):
    return emoji.get_emoji_regexp().sub(r'', text.decode('utf8'))
def summarization_func(hashtag,bodytext):
    # encode the text into tensor of integers using the appropriate tokenizer
    inputs = tokenizer.encode("summarize: " + bodytext[:5000], return_tensors="pt", max_length=700, truncation=True)
    # generate the summarization output
    outputs = model.generate(
        inputs, 
        max_length=240, 
        min_length=40, 
        length_penalty=2.0, 
        num_beams=4, 
        early_stopping=True)
    output = tokenizer.decode(outputs[0])
    publish_tweet(output,hashtag)
    return output
def publish_tweet(output,hashtag):
    if hashtag[0] == '#':
        output = output +' '+str(hashtag)
    else:
        hashtag = hashtag.replace(' ','_')
        output = output + ' #'+str(hashtag)
    print(output)
    try:
        api.update_status(output)
    except:
        pass
def get_link():
    time.sleep(5)
    driver.switch_to_window(driver.window_handles[1])
    bodyText = driver.find_element_by_tag_name("body").text
    link=driver.current_url
    time.sleep(5)
    driver.close()
    driver.switch_to_window(driver.window_handles[0])
    return link,bodyText
hostname="one.one.one.one"
options=webdriver.ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.22 Safari/537.36'
port_number = find_free_port() #Calling function to check availables port on localhost to run the chrome instance on
port_url = "--remote-debugging-port=" + str(port_number) #Use the available port number to assign to chrome instance
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument(f'user-agent={user_agent}') #User agent is added
options.add_argument(port_url) #Port is given
options.add_argument("--disable-renderer-backgrounding")#Set the priority(low, medium, high) of chrome instances(Generally runs on low but using this, it runs on Medium priority)
options.add_argument("enable-features=NetworkServiceInProcess")
options.add_argument("--disable-dev-shm-usage")#Handles chrome instance crash
options.add_argument("--disable-gpu")# Temporarily needed if running on Windows
options.add_argument("--disable-features=VizDisplayCompositor")#Time out error
options.add_argument("start-maximized")
options.add_argument("--headless")#Open headless chrome instance
options.add_argument("--no-sandbox")#Required to efficiently open headless chrome
driver=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=options)
url = "http://localhost:" + str(port_number)#localhost string and port number to assign to pychrome so that we can use chrome developer tools and everything with separate instances on different port numbers(Each instances is separate from the others)
dev_tools = pychrome.Browser(url=url)#enables dev_tools to use on each instance
tab = dev_tools.list_tab()[0]#[0] represents first tab in every chrome instance
tab.start()#=starts the tab

india_trends = api.trends_place(2282863,)[0]['trends'][:25]

text_list = []
hashtags_list = []
message = ''

try:
    for i in india_trends:
        hashtag = str(i['name'])
        if i['name'][0] == '#':
            temp = str(i['name'])[1:] 
        else:
            temp = str(i['name'])
        lang = TextBlob(temp)
        if lang.detect_language() == 'en':
            driver.get("https://news.google.com/topstories?hl=en-IN&gl=IN&ceid=IN:en")
            time.sleep(5)
            google_news = driver.find_element_by_xpath("//a[@title='News']")
            action = webdriver.common.action_chains.ActionChains(driver)
            action.move_to_element_with_offset(google_news, 500, 0)
            action.click()
            action.send_keys(temp)
            action.send_keys(Keys.ENTER)
            action.perform()
            time.sleep(5)
            bodyText = driver.find_element_by_tag_name("body").text
            if 'No results found.' not in bodyText:
                try:
                    link_element = driver.find_element_by_xpath('//*/div[2]/div[2]/div/main/c-wiz/div[1]/div[1]/div/div/article/a').click()
                    url_temp,btext = get_link()
                    print(url_temp)
                    text_list.append(btext)
                    hashtags_list.append(hashtag)
                    time.sleep(5)
                except Exception:
                    print('Element not found')
                    pass
                try:
                    link_element = driver.find_element_by_xpath('//*/div[2]/div[2]/div/main/c-wiz/div[1]/div[1]/a').click()
                    url_temp,btext = get_link()
                    print(url_temp)
                    text_list.append(btext)
                    hashtags_list.append(hashtag)
                    time.sleep(5)
                except Exception:
                    print('Element not found')
                    pass
                try:
                    link_element = driver.find_element_by_xpath('//*/div[2]/div[2]/div/main/c-wiz/div[1]/div[1]/div/article/a').click()
                    url_temp,btext = get_link()
                    print(url_temp)
                    text_list.append(btext)
                    hashtags_list.append(hashtag)
                    time.sleep(5)
                except:
                    print('Element not found')
                    pass
            else:
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)
                tweet = tw.Cursor(api.search,q=hashtag,lang="en",since=yesterday,tweet_mode='extended').items(1000)
                tweet_list = []
                for t in tweet:
                    if (not t.retweeted) and ('RT @' not in t.full_text) and (t.user.followers_count > 100):
                        without_emoji = give_emoji_free_text(t.full_text.encode('utf8','strict'))
                        without_hashtags = without_emoji.replace(str(hashtag),"")
                        without_all_hashtags = ' '.join(x for x in without_hashtags.split() if not x.startswith('#'))
                        without_all_attherate = ' '.join(x for x in without_all_hashtags.split() if not x.startswith('@'))
                        tweet_list.append(without_all_attherate)
                one_string=''
                for l in tweet_list:
                    without_link = ' '.join(x for x in l.split() if not x.startswith('http'))
                    one_string = one_string+str(without_link)
                text_list.append(btext)
                hashtags_list.append(hashtag)
except:
    pass
driver.close()
driver.quit()

for i in range(len(text_list)):
    summarization_func(hashtags_list[i],text_list[i])
