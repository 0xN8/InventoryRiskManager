from tools.config import url, coin, testUrl, coinShort
from models.defaults import hyperInvRiskDefaults
from trading.trade import trade
from calc.beta import betaScanner




def main():
    hyperClass = hyperInvRiskDefaults(url)
    bestBeta = betaScanner(hyperClass, coin)
    # trade(hyperClass, coin, bestBeta, coinShort)
    
main()