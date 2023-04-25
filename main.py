import itertools
from requests import get
import json
from lxml import html
from datetime import datetime, timedelta
import discord, os
from typing import List, Tuple
from dotenv import load_dotenv


class AlerTender:
    URL: str = 'https://www.tender.gov.mn/mn/invitation'
    CONFIG_FILE: str = 'config.json'
    CONFIG: dict = {}
    UPLOADED: list = []

    def __init__(self) -> None:
        load_dotenv()
        self.read_config()
        for page in itertools.count(1):
            tree = html.fromstring(
                get(f'{self.URL}?year={datetime.now().year}&month={datetime.now().month}&perpage=100&page={page}').content)
            if self.process_tenders(tree):
                break
        self.write_config()

    def read_config(self) -> None:
        with open(self.CONFIG_FILE, 'r') as f: self.CONFIG = json.load(f)

    def write_config(self) -> None:
        self.CONFIG['uploaded'] += self.UPLOADED
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.CONFIG, f, ensure_ascii=False, indent=2)

    def process_tenders(self, tree) -> bool:
        for tender in tree.xpath("//div[@id='tender-result-table']//tr"):
            try:
                _date = tender.xpath(
                    ".//div[@class='date']")[0].text_content().strip()
                _id = tender.xpath(
                    ".//a[@class='tender-name']")[0].get('href').split('/')[-1]

                # imagine script runs every day so you can `datetime.now().day - 1` -5 is just in case
                if datetime.strptime(_date, '%Y-%m-%d') < datetime.now() - timedelta(days=5):
                    print('Breaking')
                    return True
                if _id in self.CONFIG['uploaded']:
                    continue
                print(f'[*] Processing: {_id}')
                _tree = html.fromstring(
                    get(f'{self.URL}/detail/{_id}').content)
                content = _tree.xpath(
                    "//div[contains(@class, 'tender-info-content')]")[0].text_content()
                is_fine, keywords = self.check_content(content)
                if is_fine:
                    title = _tree.xpath(
                        "//span[@class='tagStyleClass']")[1].text_content()
                    price = " ".join(_tree.xpath(
                        "//div[@class='tender-info-detail']//div[6]")[0].text_content().split())
                    self.discord_log(
                        f"{self.URL}/detail/{_id}",
                        f"[+] Гарчиг     : {title}\n[+] Үнэ        : {price}\n[+] Түлхүүр үг : {','.join(keywords)}\n{content}"
                    )
                    self.UPLOADED.append(_id)
            except Exception as e:
                self.discord_log('ERROR', e)
                return True
        return False

    def check_content(self, content) -> Tuple[bool, List[str]]:
        keywords = [keyword for keyword in self.CONFIG['keywords'] if keyword in content]
        return bool(keywords), keywords

    # you can update your logging logic
    def discord_log(self, link, resp) -> None:
        TOKEN = os.environ.get('DISCORD_TOKEN')
        CHANNEL = int(os.environ.get('CHANNEL'))
        client = discord.Client(intents=discord.Intents.default())

        @client.event
        async def on_ready() -> None:
            await client.get_channel(CHANNEL).send(f'{link}\n```{resp[:1900]}```')
            await client.close()

        client.run(TOKEN)


if __name__ == '__main__':
    AlerTender()
