from dynamic_fetch import DynamicFetcher
from static_fetch import StaticFetcher
from rich.console import Console    
from rich.panel import Panel    
from rich.prompt import Prompt
import requests
import os

console = Console()

def static_fetch(modifier: str, isImage: bool):
    file_path = f"../data/page_sources/{modifier.replace('/', '_')}.html"
    if not os.path.exists(file_path):
        console.print(Panel("[red]Dynamic fetch is needed.[/]"),justify="center")
        return
    sfetcher = StaticFetcher(content=open(file_path), modifier=modifier)
    try:
        sfetcher.dump_json(isImage)
    except Exception as e:
        console.print(Panel(f"[red]Error {e}[/]"),justify="center")
        return 

def dynamic_fetch(url, modifier, num, xpath):
    dfetcher = DynamicFetcher(url=url, modifier=modifier)
    content = dfetcher.fetch(xpath=xpath,min_num=num)
    dfetcher.save_html(content=content)

def main():
    base_url = "https://www.aarong.com/"
    base_xpath = "//li[@class='item product product-item']"
    while True:
        console.print("[italic green]Press q to quit[/]")

        modifier = Prompt.ask("Paste the modifier")
        if modifier.lower() == "q":
            break
        if modifier == "":
            break
        if requests.get(base_url + modifier).status_code != 200:
            console.print(Panel("[red]Invalid URL[/]"),justify="center")
            continue
        
        while True:
            console.print("[italic green]Press c to change modifier[/]")

            choice = Prompt.ask("Choose the type of fetch", choices=["static", "dynamic","c"])
            if choice == "c":
                break

            if choice == "static":
                with_img = Prompt.ask("Download Image?", choices=["yes", "no"]) == "yes"
                static_fetch(modifier,with_img)
            
            if choice == "dynamic":
                total_tags = int(Prompt.ask("Number of product to list", default=60))
                dynamic_fetch(base_url, modifier, total_tags, base_xpath)

if __name__ == "__main__":
    main()