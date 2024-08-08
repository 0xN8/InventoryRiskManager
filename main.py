from tools.config import coin, coinShort, url, testUrl, wsUrl, wsTestUrl
from models.defaults import hyperInvRiskDefaults
from trading.trade import trade, hedge_thread
from calc.beta import betaScanner




def main():
    hyperClass = hyperInvRiskDefaults(url, prod = True)
    bestBeta = betaScanner(hyperClass, coin)
    hedge_thread(hyperClass, bestBeta)
    
main()