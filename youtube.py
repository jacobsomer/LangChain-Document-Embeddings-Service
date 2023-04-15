# importing the libraries
from bs4 import BeautifulSoup
import requests
  
# creating function
def scrape_youtube_info(url):
      
    # getting the request from url
    r = requests.get(url)
      
    # converting the text
    s = BeautifulSoup(r.text, "html.parser")
      
    # finding meta info for title
    title = s.find("span", class_="watch-title").text.replace("\n", "")
      
    # finding meta info for views
    views = s.find("div", class_="watch-view-count").text
      
    # finding meta info for likes
    likes = s.find("span", class_="like-button-renderer").span.button.text
      
    # saving this data in dictionary
    data = {'title':title, 'views':views, 'likes':likes}
      
    # returning the dictionary
    return data