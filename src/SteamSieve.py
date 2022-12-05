
from bs4 import BeautifulSoup as BS


class Sieve:

    @staticmethod
    def getItemNameID(page) -> str:

        soup = BS(page, "html.parser")
        scs = soup.find_all('script')
        clue = "Market_LoadOrderSpread"
        for s in scs:
            txt = s.text
            idx = txt.find(clue)

            if idx != -1:
                e_bracket = (txt[idx+len(clue):len(txt)]).find(")")
                return str(txt[idx + len(clue) + 1:idx + len(clue) + e_bracket]).strip()




