from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from os.path import abspath,join,dirname
from typing import List
from time import sleep
from rich.console import Console
import random
import os

console = Console()

class DynamicFetcher:

    def __init__(self,url: str, modifier: str = "", *options_arg: str) -> None:
        self.additonal_arg: List[str] = list(options_arg)
        self.url = url
        self.modifier = modifier
        self.options: Options = self._set_options()
        self.service: Service = self._set_service()
        self.driver: Chrome = None


    def _set_options(self):

        options: Options = Options()
        for arg in self.additonal_arg:
            options.add_argument(arg)
        return options
    

    def _set_service(self):

        chromeDriverPath: str = abspath(join(dirname(__file__),"chromedriver"))
        service: Service = Service(executable_path=chromeDriverPath)
        return service
    
    def _get_driver(self):

        if not self.driver:
            self.driver: Chrome = Chrome(options=self.options,service=self.service) 
            # return self.driver
        
    def _count_condition(self,xpath: str, min_num: int):
        
        tags = self.driver.find_elements(By.XPATH,xpath)
        console.print(f"Found [bold blue]{len(tags)}[/] tags")

        return len(tags) >= min_num 
        


    def _scroll_page(self, xpath: str, min_num: int):
        scroll_num = 1
        while True:
            if self._count_condition(xpath, min_num):
                break
            self.driver.execute_script("scrollTo(0, window.scrollY + window.innerHeight*2)")
            console.print(f"Scrolled [bold blue]{scroll_num}[/bold blue] time(s)")
            scroll_num += 1
            sleep(random.randint(5,10))
            


        
    def fetch(self, xpath: str, min_num: int = 60):

        self._get_driver()
        self.driver.get(self.url+self.modifier)
        console.print(f"Redirecting to [bold blue]{self.url+self.modifier}[/]")
        sleep(2)

        self._scroll_page(xpath=xpath,min_num=min_num)
        WebDriverWait(driver=self.driver,timeout=20).until(lambda _: self._count_condition(xpath=xpath,min_num=min_num))


        return self.driver.page_source
    

    def _dir_maker(self):

        os.makedirs(f"../data/page_sources/", exist_ok=True)
        page_dir = f"../data/page_sources/{self.modifier.replace('/','_')}.html"

        return page_dir

    def save_html(self, content):
        file_path = self._dir_maker()
        with open(file_path, "w") as file:
            file.write(BeautifulSoup(content, 'html.parser').prettify())        
        
    def driver_quit(self):
        if self.driver:
            self.driver.quit()


if __name__ == "__main__":
    dfethcer = DynamicFetcher(url="https://www.aarong.com/", modifier="men/panjabi")
    content = dfethcer.fetch(xpath="//li[@class='item product product-item']", min_num=18)
    dfethcer.save_html(content)
    dfethcer.driver_quit()