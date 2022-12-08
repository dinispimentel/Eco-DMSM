import os

# CACHE_DIR = "C:\\Users\\dinis\\Desktop\\EcoScraper\\DMSM\\src\\" + "cache\\"
CACHE_DIR = os.path.dirname(__file__) + "/cache/"

class Config:

    class ENV:
        URL_PPREFIX = "http://"
        LOCAL_IP = "192.168.0.120"

    class ExRates:
        PORT = 8085
        BASE = "EUR"

    class Proxying:

        TIME_OUT = (5, 5)  # write, read
        REUSABILITY_TIMEOUT = 10  # secs
        WAIT_FOR_PROXIES_TO_BE_REUSABLE_TIMER = 30
        TIME_OUT_STACKABLE_LOCK = 30  # isto * num de tentativas em segundos
        TOO_MANY_REQUESTS_STACKABLE_LOCK = 60
        FATAL_LOCK = 30

        class StrikeLimit:
            TIME_OUT = 7
            FORBIDDEN = 3
            TOO_MANY_REQUESTS = 10
            FATAL = 3

        class Files:

            PROXY_ORCHESTRATOR_CACHE = CACHE_DIR + "proxy_orchestrator.json"


    class DMarket:

        class APIKeys:

            PUBLIC = "810826ff9ff31c940addb12c0306a0ab12bfb14d7a1004a11fbdf1347b0e8ef9"
            PRIVATE = "cf3c62ae1b02fe7f2e388b29c8725cdfa1c0871ceaaf5dccc8bfb1cb8dbb4feb810826ff9ff31c940addb12c0306a0ab12bfb14d7a1004a11fbdf1347b0e8ef9"


        class Offering:

            INSTANCES = 1
            MAX_RETRIES = 3
            TOO_MANY_REQUESTS_DELAY = 1.5  # segundos
            DELAY_CONFIG = {
                "delay": 1.2,
                "instances_before_delay": 1
            }

            class Constrains:
                """Para uso do updateinternaldmarketdata"""
                ALLOWED_TYPES = ["dmarket", "p2p"]
                ALLOWED_TF_CATEGORIES_PATH = ["knife", "rifle", "sniperrifle", "pistol", "smg", "shotgun", "machinegun"]
                MAX_SINGLE_MAX_LIMIT = 500
        class OfferBook:

            class Files:

                @staticmethod
                def getSaveDir(testing=False):
                    f = "dmofferbook"
                    return CACHE_DIR + f + ".json" if not testing else CACHE_DIR + f + "-testing" + ".json"


    class Steam:

        class ItemNaming:

            INSTANCES = 25  # 15
            MAX_RETRIES = 3
            FORBIDDEN_TIMEOUT = 10
            DELAY_CONFIG = {
                "delay": 1,  # 1.5
                "instances_before_delay": 50  # 30
                            }
            ANNOTATE_IMMEDIATELY = True

        class SkinPricing:
            INSTANCES = 25
            MAX_RETRIES = 3
            FORBIDDEN_TIMEOUT = 15  # em segundos
            DELAY_CONFIG = {
                "delay": 1,
                "instances_before_delay": 50
            }

    class CurrencyConversion:
        AVAILABLE_CURRENCIES = ["ARS", "USD", "EUR", "TRY"]

    class Redis:
        HOST = 'localhost'
        PORT = 6379

    @staticmethod
    def buildExRatesURL(path):
        return Config.ENV.URL_PPREFIX + Config.ENV.LOCAL_IP + ":" + str(Config.ExRates.PORT) + path



