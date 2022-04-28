from math import log, sqrt, pi, exp
from scipy.stats import norm
from datetime import datetime, date
import numpy as np
import pandas as pd
from pandas import DataFrame

#https://medium.com/swlh/calculating-option-premiums-using-the-black-scholes-model-in-python-e9ed227afbee

#S = Preço da ação base
#K = Strike da opção
#T = Tempo até o vencimento em proporção ao ano (1 = 1 ano)
#r = selic diaria em decimal
#sigma = volatilidade de ação base em decimal (29% = 0.29)

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

    def call_delta(self, S, K, T, r, sigma):
        return norm.cdf(self.d1_fun(S,K,T,r,sigma))
    def call_gamma(self, S, K, T, r, sigma):
        return norm.pdf(self.d1_fun(S,K,T,r,sigma))/(S*sigma*sqrt(T))
    def call_vega(self, S, K, T, r, sigma):
        return 0.01*(S*norm.pdf(self.d1_fun(S,K,T,r,sigma))*sqrt(T))
    def call_theta(self, S, K, T, r, sigma):
        return ((-(S*norm.pdf(self.d1_fun(S,K,T,r,sigma))*sigma)/(2*sqrt(T))) - (r*K*exp(-r*T)*norm.cdf(-self.d2_fun(S,K,T,r,sigma))))/252
    def call_rho(self, S, K, T, r, sigma):
        return 0.01*(K*T*exp(-r*T)*norm.cdf(self.d2_fun(S,K,T,r,sigma)))
        
    def put_delta(self, S, K, T, r, sigma):
        return -norm.cdf(-self.d1_fun(S,K,T,r,sigma))
    def put_gamma(self, S, K, T, r, sigma):
        return norm.pdf(self.d1_fun(S,K,T,r,sigma))/(S*sigma*sqrt(T))
    def put_vega(self, S, K, T, r, sigma):
        return 0.01*(S*norm.pdf(self.d1_fun(S,K,T,r,sigma))*sqrt(T))
    def put_theta(self, S, K, T, r, sigma):
        return ((-(S*norm.pdf(self.d1_fun(S,K,T,r,sigma))*sigma)/(2*sqrt(T))) + (r*K*exp(-r*T)*norm.cdf(-self.d2_fun(S,K,T,r,sigma))))/252
    def put_rho(self, S, K, T, r, sigma):
        return 0.01*(-K*T*exp(-r*T)*norm.cdf(-self.d2_fun(S,K,T,r,sigma)))
