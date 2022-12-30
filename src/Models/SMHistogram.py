from typing import List, Tuple


class Histogram:

    def __init__(self, buy_offer_book, sell_offer_book, bid, ask, currency="USD/EUR/ARS?"):

        self.buy_offer_book: List[Tuple[float, int]] = buy_offer_book
        self.sell_offer_book: List[Tuple[float, int]] = sell_offer_book
        self.bid = float(bid)
        self.ask = float(ask)
        self.currency = currency


    @staticmethod
    def build_raw_histogram(raw: dict, max_entries: int = None, currency: str = "USD/EUR/ARS?"):


        b_o_g = raw.get("buy_order_graph")
        bg = []
        mbe = max_entries+1 if (max_entries is not None) and max_entries < len(b_o_g) else len(b_o_g)
        for bo_idx in range(0, mbe):
            bg.append([b_o_g[bo_idx][0], b_o_g[bo_idx][1]])


        s_o_g = raw.get("sell_order_graph")
        sg = []
        mse = max_entries+1 if (max_entries is not None) and max_entries < len(s_o_g) else len(s_o_g)
        for so_idx in range(0, mse):
            sg.append([s_o_g[so_idx][0], s_o_g[so_idx][1]])

        try:
            highest_buy_order = float(raw.get("highest_buy_order"))/100
        except TypeError:
            highest_buy_order = 0
        try:
            lowest_sell_order = float(raw.get("lowest_sell_order"))/100
        except TypeError:
            lowest_sell_order = 0

        return Histogram(bg, sg, highest_buy_order, lowest_sell_order, currency=currency)


    def toDICT(self):
        return self.__dict__

    def print(self, max_entries=5):

        print("BUY:")
        buy_entries_shown = 0
        for b_o in self.buy_offer_book:
            if buy_entries_shown < max_entries:
                print(f'{b_o[0]} {self.currency} | Amt: {b_o[1]}')
            buy_entries_shown += 1
        print("----------")
        print("SELL:")
        sell_entries_shown = 0
        for s_o in self.sell_offer_book:
            if sell_entries_shown < max_entries:
                print(f'{s_o[0]} {self.currency} | Amt: {s_o[1]}')
            sell_entries_shown += 1


