from math import log, sqrt, pi, exp
from scipy.stats import norm
from datetime import datetime, date
import numpy as np
import pandas as pd
from pandas import DataFrame

#https://medium.com/swlh/calculating-option-premiums-using-the-black-scholes-model-in-python-e9ed227afbee

#S = Preço da ação base
#K = Strike da opção
#T = Tempo até o vencimento
#r = selic
#sigma = volatilidade de ação base

#Função pré-requisito
class bs:
    def __init__(self):
        self.i = 1

    def d1_fun(self, S,K,T,r,sigma):
        return(log(S/K)+(r+sigma**2/2.)*T)/(sigma*sqrt(T))
    def d2_fun(self, S,K,T,r,sigma):
        return self.d1_fun(S,K,T,r,sigma)-sigma*sqrt(T)

    #Calculo de Black-Scholes
    #Ex bsVal = round(bs().bs_call(self.valorAtivoBase, l.option_strike, self.tempoVencimento, self.selic, self.sigma), 3)
    def bs_call(self, S, K, T, r, sigma):
        return S * norm.cdf(self.d1_fun(S,K,T,r,sigma)) - K * exp(-r * T) * norm.cdf(self.d2_fun(S,K,T,r,sigma))

    def bs_put(self, S, K, T, r, sigma):
        return K * exp(-r * T) - S + self.bs_call(S, K, T, r, sigma)

    def call_implied_volatility(self, Price, S, K, T, r):
        if not Price:
            return "Not Calc"
        else:
            passo = 5
            sigma = 5
            Price_implied = self.bs_call(S, K, T, r, sigma)
            while (abs(Price-Price_implied) > 0.005) and (passo > 0.001):
                passo = passo/2
                if Price>Price_implied:
                    sigma = sigma + passo
                else:
                    sigma = sigma - passo
                Price_implied = self.bs_call(S, K, T, r, sigma)
                #print("P:{} PI:{} S:{} Ps:{}".format(Price, Price_implied, sigma, passo))
            if sigma < 0.0001:
                return 0
            else:
                return round(sigma, 4)

    def put_implied_volatility(self, Price, S, K, T, r):
        if not Price:
            return "Not Calc"
        else:
            passo = 5
            sigma = 5
            Price_implied = self.bs_put(S, K, T, r, sigma)
            while (abs(Price-Price_implied) > 0.005) and (passo > 0.001):
                passo = passo / 2
                if Price > Price_implied:
                    sigma = sigma + passo
                else:
                    sigma = sigma - passo
                Price_implied = self.bs_put(S, K, T, r, sigma)
                #print("P:{} PI:{} S:{} Ps:{}".format(Price, Price_implied, sigma, passo))
            if sigma < 0.0001:
                return 0
            else:
                return round(sigma, 4)
