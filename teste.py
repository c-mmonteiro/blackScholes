from bs import *

#S = Preço da ação base
S = 49
#K = Strike da opção
K = 50
#T = Tempo até o vencimento
T = 0.3846
#r = selic 
r = 0.05#(((1 + 0.05) ** (1 / 12)) - 1)
#sigma = volatilidade de ação base
sigma = 0.20

Price = 1.2


print(f'Premio da opção: {bs().bs_put(S,K, T, r, sigma)}')
print(f'Vol Imp: {bs().put_implied_volatility(Price, S, K, T, r)}')
print(f'Delta: {bs().put_delta(S,K, T, r, sigma)}')
print(f'Gamma: {bs().put_gamma(S,K, T, r, sigma)}')
print(f'Theta: {bs().call_theta(S,K, T, r, sigma)}')
print(f'Vega: {bs().put_vega(S,K, T, r, sigma)}')
print(f'Rho: {bs().put_rho(S,K, T, r, sigma)}')


