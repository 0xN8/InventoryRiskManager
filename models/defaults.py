from tools.utils import setup
class hyperInvRiskDefaults:
    def __init__(self, url, prod =True):
        self.account, self.accAddress, self.neuAddress, self.info, self.exchange = setup(url, prod)