# Twitter_bot

This is a Twitter bot that retrieves trending hashtags and topics using Tweepy. With the help of Selenium, it would search trending topics on Google News and scrap the websites shown in the result. For topics without any search results on Google News, tweets made by others on the same topic will be retrieved. Retrieved text will be summarized using T5 transformer. The summarized text has to be lower than the tweeter's required length. 
