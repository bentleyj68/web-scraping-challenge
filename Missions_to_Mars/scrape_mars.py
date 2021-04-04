# Import all the libraries required for the web scraping
from splinter import Browser
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def init_browser():
    # Use the Chrome browser installed on the system and initialise
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=True)

def scrape():
    ### Scrape function for all Mars information ### 
    browser = init_browser()
    # Dictionary to hold all return values
    mars_data = {}

    ## NASA Mars News
    # URL of page to be scraped
    url_news = 'https://mars.nasa.gov/news/'
    # Retrieve page with the requests module
    response = requests.get(url_news)
    # Create BeautifulSoup object; parse with 'lxml'
    soup_news = BeautifulSoup(response.text, 'lxml')
    mars_data['news_title'] = soup_news.find('div', class_='content_title').text.replace('\n',"")
    mars_data['news_p'] = soup_news.find("div", class_="rollover_description_inner").text.replace('\n',"")
    
    ## JPL Mars Space Images - Featured Image
    url_image = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url_image)
    time.sleep(1)
    # Use B.Soup to scrape the page
    html= browser.html
    soup = BeautifulSoup(html, "html.parser")
    browser.links.find_by_partial_text('FULL IMAGE')
    for link in soup.find_all('img'):
        if(link.get('src').startswith( 'image/featured')):
            mars_data['featured_image_url'] = f"https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{link.get('src')}"

    ## Mars Facts
    url_facts = 'https://space-facts.com/mars/'
    tables = pd.read_html(url_facts)
    facts_table = pd.DataFrame(tables[0])
    facts_table.rename(columns = {0: "Fact", 1: "Value"}, inplace=True)
    facts_table.set_index("Fact", inplace=True)
    table_html = facts_table.to_html()
     
    #  Clean the HTML table
    table_html= table_html.replace('\n',"")
    mars_data['facts_table'] = table_html


    ## Mars Hemispheres
    url_hemispheres = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url_hemispheres)
    html = browser.html
    soup_hemispheres = BeautifulSoup(html, 'html.parser')

    products = soup_hemispheres.find_all('div', class_='item')

    products_links = []

    for product in products:
        heading = product.find('h3').text
        product_link = \
        f"https://astrogeology.usgs.gov{product.find('a', class_='itemLink product-item')['href']}.tif"
        
        products_links.append({"title" : heading, "img_url" : product_link})

    mars_data['product_links'] = products_links

    browser.quit()
    return mars_data
