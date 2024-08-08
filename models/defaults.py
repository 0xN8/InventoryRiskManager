from tools.utils import setup
class hyperInvRiskDefaults:
    def __init__(self, url, prod):
        self.account, self.accAddress, self.makerAddress, self.hedgeAddress, self.info, self.exchange = setup(url, prod)