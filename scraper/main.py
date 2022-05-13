import requests
from bs4 import BeautifulSoup
import pandas as pd

class Scraper():
  def __init__(self, url: str):
    self.url = url
    self.car_kind_links = []
    self.car_kind_names = []
    self.data = pd.DataFrame(columns=['kind', 'name', 'image_url', 'start_year', 'end_year', 'doors'])
  
  def run(self):
    self._get_car_kind_link()
    for index in range(len(self.car_kind_links)):
      kind = self.car_kind_names[index]
      link = self.car_kind_links[index]
      self._scrape_car_pages(link, kind)
  
  def save(self):
    self.data.to_csv("data/car.csv", index=False)

  def _get_soup(self, url: str) -> BeautifulSoup:
    """
    Get the soup from the url
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup
    
  def _get_car_kind_link(self) -> list:
    """
    Get the car types links from the main url
    """
    soup = self._get_soup(self.url)
    car_kind = soup.select("section.carbody div.row > div.col-4 > a")
    for car_type in car_kind[0:5]:
      self.car_kind_links.append(car_type['href'])
      self.car_kind_names.append(car_type.text)

  def _get_maximum_page_number(self, url: str) -> int:
    """
    Find the maximum page number for the car type
    """
    soup = self._get_soup(url)
    last_link_element = soup.select("section.models > p.links")[-1]
    last_page_number = last_link_element.text.split("next")[-1].strip()[1:-1]
    return int(last_page_number)

  def _scrape_car_pages(self, url: str, kind: str):
    last_page_number = self._get_maximum_page_number(url)
    print(f"Scraping car type: {kind} - Start")
    for page_index in range(1, last_page_number+1):
      print(f"Page {page_index} - Start")
      page_url = f"{url[:-5]}/page{page_index}.html"
      soup = self._get_soup(page_url)
      car_list = soup.select("section.models div.col-4")
      for car in car_list:
        car_image_url = self.url + car.find("img")['src']
        car_name = car.find("a").text.strip()
        car_metadata = car.find("p").get_text(separator=" ").strip().split(" ")
        car_start_year = car_metadata[0]
        car_end_year = car_metadata[2]
        car_doors = car_metadata[3]
        scraped_data = pd.DataFrame({
          'kind': [kind],
          'name': [car_name],
          'image_url': [car_image_url],
          'start_year': [car_start_year],
          'end_year': [car_end_year],
          'doors': [car_doors]
        })
        self.data = pd.concat([self.data, scraped_data], ignore_index=True)
      print(f"Page {page_index} - Done")
    print(f"Scraping car type: {kind} - Done")

# Start running the scraper
main_url = "https://www.cars-data.com"

scraper = Scraper(main_url)

scraper.run()

scraper.save()

print(scraper.data)
