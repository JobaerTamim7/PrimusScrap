from bs4 import BeautifulSoup
import requests
from rich.console import Console
import os
import pandas as pd
from time import sleep
import re
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 

console = Console()

class StaticFetcher:
    def __init__(self, content : str, modifier: str="") -> None:
        self.content = content
        self.soup = self._make_soup()
        self.modifier = modifier
        self.driver = Chrome(service=Service(executable_path=os.path.abspath(os.path.join(os.path.dirname(__file__),"chromedriver"))),options=self._get_options())


    def _make_soup(self):
        return BeautifulSoup(self.content, 'html.parser')
    

    def _get_options(self):
            
            options = Options()
            options.add_argument("--headless")
            return options
    


    def _get_links(self):

        anchor_tags = self.soup.find_all("a", class_="product photo product-item-photo")
        anchor_srcs = [src.get("href") for src in anchor_tags]

        return anchor_srcs


    def mkdirs_img(self):

        file_path = f"../data/img_pool/{self.modifier}/"
        os.makedirs(file_path, exist_ok=True)

        return file_path

    
    def get_img(self, img_op_url: str, file_name)-> bool:

        console.print(f"[green]Downloading Image {file_name}[/]")
        response = requests.get(img_op_url)
        path = self.mkdirs_img()
        file_name = re.sub(r'\/', ' ', file_name)
        with open(path + file_name, "wb") as file:
            file.write(response.content)

        return True


    def get_img_url(self, soup: BeautifulSoup):


        img_tag = soup.find("img", class_="fotorama__img")
        if img_tag:
            img_url = img_tag.get("src")
            img_url = re.sub(r"\?optimize=.*", "", img_url)
            return img_url

        return None



    def get_product_info(self, isImage: bool = False):

        links = self._get_links()
        info_list = []
        for index,link in enumerate(links):
            console.print(f"Redirecting to [green]{link}[/]")
            self.driver.get(link)
            sleep(1)
            product_page_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            # with open("test.html","w") as file:
            #     file.write(product_page_soup.prettify())

            info_dict = {}

            product_table = product_page_soup.find("table", class_="data table additional-attributes")
            table_rows = product_table.find_all("tr")
            product_name = product_page_soup.find("span", class_="base").text
            product_price = product_page_soup.find("span", class_="price").text
            product_description = product_page_soup.find("div", class_="product attribute description")
            product_description = product_description.find("div", class_="value").text
        
            img_url = self.get_img_url(product_page_soup)
            if not img_url:
                console.print(f"[red]No Image Found for {product_name}[/]\n")
                continue 
            if isImage:
                img_file_name = str(product_name)+ ".jpg"
                self.get_img(img_url, img_file_name)
                info_dict["Image File Name"] = img_file_name
                info_dict["Image Category"] = self.modifier.split('/')[0]


            info_dict["Image URL"] = img_url
            info_dict["Product Price"] = product_price
            info_dict["Product Name"] = product_name
            info_dict["Description"] = product_description
            for row in table_rows:
                key = row.find("th").text
                value = row.find("td").text
                info_dict[key] = value
            info_list.append(info_dict)
            console.print(f"[green]Product {index+1}[/] [blue]{product_name}[/] [green]Fetched[/]\n")
        return info_list
    
    def driver_quit(self):
        if self.driver:
            self.driver.quit()
    


    def mkdirs(self):
        os.makedirs(f"../data/json_pool/{self.modifier.split('/')[0]}/", exist_ok=True)
        dir = f"../data/json_pool/{self.modifier}.json"
        return dir
    


    def format_file(self, dir: str):
        with open(dir,"r+") as file:
            data = file.read()
            formatted_data = data.replace("\\/", "/")
            file.seek(0)
            file.write(formatted_data)
            file.truncate()
            console.print(f"[green]File Formatted[/]")
    


    def dump_json(self, isImage: bool = False):
        info_list = self.get_product_info(isImage)
        dir = self.mkdirs()
  
        df = pd.DataFrame(info_list)
        df.to_json(dir, orient="records", indent=4)
        self.format_file(dir=dir)
        



    