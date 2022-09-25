import tkinter as tk
from tkinter import *

import MetaTrader5 as mt5

from datetime import datetime, timedelta
import pytz

import numpy as np
import math

from bs import *


class Calculadora_BS:
    def __init__(self, juros, diasVol):

        self.juros = juros
        self.diasVol = diasVol

        self.timezone = pytz.timezone("ETC/UTC")
        self.hoje = datetime.today()
        
        #Cria Janela
        self.root = Tk()
        self.root.title('Calculadora Black and Scholes')
        self.root.geometry("500x400")

        self.lbl_input_ativo = tk.Label(self.root, width=16, height = 1, anchor='w', text="Codigo da Opção:")
        self.lbl_input_ativo.place(y = 10, x = 50)

        self.input_ativo = tk.Text(self.root, width = 10, height = 1)
        self.input_ativo.insert(INSERT, "BBASJ418")
        self.input_ativo.place(y = 30, x = 50)

        self.btn_input_ativo = Button(self.root, text="Calcular", command=self.pegar_dados)
        self.btn_input_ativo.place(y = 30, x = 180)

        self.root.mainloop()

    def pegar_dados(self):

        #Inicializa Metatrader 5
        if not (mt5.initialize()):
            print(f'Problema ao inicializar o terminal, error: {mt5.last_error()}')
            if mt5.shutdown():
                print(f'O terminal foi finalizado.')
            else:
                print(f'Problema ao finalizar o terminal, error: {mt5.last_error()}')

        codigo = self.input_ativo.get("1.0", "end-1c")

        info = mt5.symbol_info(codigo)

        self.tipo = ["CALL", "PUT"][info.option_right == 1]
        self.vencimento = datetime.utcfromtimestamp(info.expiration_time)
        self.strike = info.option_strike
        if info.last == 0:
            valBase = mt5.copy_rates_from_pos(codigo, mt5.TIMEFRAME_D1, 0, 1)
            self.ultimo = valBase[0]['close']
        else:
            self.ultimo = info.last

        ####### - Impressão dos dados basicos da opção

        self.lbl_info1 = tk.Label(self.root, width=16, height = 2, anchor='w', text=self.tipo)
        self.lbl_info1.place(y = 70, x = 50)

        data = self.vencimento.strftime('%d/%m/%Y')
        self.lbl_info2 = tk.Label(self.root, width=25, height = 1, anchor='w', text=('Vencimento: ' + data))
        self.lbl_info2.place(y = 100, x = 50)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Strike: R$" + str(self.strike))
        self.lbl_info3.place(y = 120, x = 50)

        self.lbl_info4 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Ultimo: R$" + str(self.ultimo))
        self.lbl_info4.place(y = 140, x = 50)

        ##################################################################################
        ### Ativo
        ##################################################################################

        valBase = mt5.copy_rates_from_pos(info.basis, mt5.TIMEFRAME_D1, 0, self.diasVol)
        self.valorAtivoBase = valBase[len(valBase) - 1]['close']

        #calcula a volatilidade histórica do ativo
        retornos = []
        for idx, v in enumerate(valBase):
            if idx != 0:
                retornos.append(v['close'] / valBase[idx - 1]['close'])
        retornoStd = np.std(retornos)
        soma = 0
        for r in retornos:
            soma = soma + (r - retornoStd)**2
        self.sigma_hist = np.sqrt(soma/(len(retornos)-1))

        #Calcula Volatilidade Livro Luiz Mauricio
        retornos = []
        for idx, v in enumerate(valBase):
            if idx != 0:
                retornos.append(np.log(v['close'] / valBase[idx - 1]['close']))   
 
        self.sigma_livro = np.sqrt(252) * np.std(retornos[0:self.diasVol-1])

        #EWMA
        retornos = []
        for idx, v in enumerate(valBase):
            if idx != 0:
                retornos.append(math.log(v['close'] / valBase[idx - 1]['close']))
        retornoStd = np.std(retornos)
        soma = 0
        for r in retornos:
            soma = soma + (r - retornoStd)**2
        self.ewma = np.sqrt(soma/(len(retornos)-1))


        self.ultimoAtivo = valBase[self.diasVol-1]['close']

        #### - Impressão dos dados da ação

        self.lbl_info1 = tk.Label(self.root, width=16, height = 2, anchor='w', text=info.basis)
        self.lbl_info1.place(y = 70, x = 250)

        self.lbl_info2 = tk.Label(self.root, width=25, height = 1, anchor='w', text=('Ultimo: R$ ' + str(self.ultimoAtivo)))
        self.lbl_info2.place(y = 100, x = 250)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Vol Hist: " + str(round(100*self.sigma_hist, 2)))
        self.lbl_info3.place(y = 120, x = 250)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="EWMA: " + str(round(100*self.ewma, 2)))
        self.lbl_info3.place(y = 140, x = 250)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Vol Livro: " + str(round(100*self.sigma_livro, 2)))
        self.lbl_info3.place(y = 160, x = 250)


        if not (mt5.shutdown()):
            print(f'Problema ao finalizar o terminal, error: {mt5.last_error()}')


        #####################################################################################
        #### DADOS
        #####################################################################################

        self.dias = np.busday_count(self.hoje.strftime('%Y-%m-%d'), self.vencimento.strftime('%Y-%m-%d'))
        self.lbl_info2 = tk.Label(self.root, width=30, height = 1, anchor='w', text=('Dias para o Vencimento: ' + str(self.dias)))
        self.lbl_info2.place(y = 180, x = 50)

        self.lbl_info3 = tk.Label(self.root, width=30, height = 1, anchor='w', text="Taxa de Juros: " + str(round(self.juros*100, 2)))
        self.lbl_info3.place(y = 200, x = 50)




        #################################################
        ##########  Black and Scholes   #################
        #################################################

        self.sigma = self.sigma_livro

        if self.tipo == "CALL":
            self.priceBL = bs().bs_call(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.deltaBL = bs().call_delta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.thetaBL = bs().call_theta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.gammaBL = bs().call_gamma(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.vegaBL = bs().call_vega(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.rhoBL = bs().call_rho(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)

        else:
            self.priceBL = bs().bs_put(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.deltaBL = bs().put_delta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.thetaBL = bs().put_theta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.gammaBL = bs().put_gamma(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.vegaBL = bs().put_vega(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)
            self.rhoBL = bs().put_rho(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.sigma)


        self.lbl_info1 = tk.Label(self.root, width=16, height = 1, anchor='w', text="Preço B&S: R$" + str(round(self.priceBL, 2)))
        self.lbl_info1.place(y = 240, x = 50)

        self.lbl_info2 = tk.Label(self.root, width=25, height = 1, anchor='w', text=('Delta: ' + str(round(self.deltaBL, 4))))
        self.lbl_info2.place(y = 260, x = 50)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Theta: " + str(round(self.thetaBL, 4)))
        self.lbl_info3.place(y = 280, x = 50)

        self.lbl_info1 = tk.Label(self.root, width=16, height = 1, anchor='w', text="Gamma: " + str(round(self.gammaBL, 4)))
        self.lbl_info1.place(y = 300, x = 50)

        self.lbl_info2 = tk.Label(self.root, width=25, height = 1, anchor='w', text=('Vega: ' + str(round(self.vegaBL, 4))))
        self.lbl_info2.place(y = 320, x = 50)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Rho: " + str(round(self.rhoBL, 4)))
        self.lbl_info3.place(y = 340, x = 50)




        ######################################################
        ### VI
        ######################################################
        if self.tipo == "CALL":
            self.vi = bs().call_implied_volatility(self.ultimo, self.ultimoAtivo, self.strike, self.dias/252, self.juros)
            self.deltaVI = bs().call_delta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.thetaVI = bs().call_theta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.gammaVI = bs().call_gamma(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.vegaVI = bs().call_vega(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.rhoVI = bs().call_rho(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)

        else:
            self.vi = bs().put_implied_volatility(self.ultimo, self.ultimoAtivo, self.strike, self.dias/252, self.juros)
            self.deltaVI = bs().put_delta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.thetaVI = bs().put_theta(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.gammaVI = bs().put_gamma(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.vegaVI = bs().put_vega(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)
            self.rhoVI = bs().put_rho(self.ultimoAtivo, self.strike, self.dias/252, self.juros, self.vi)

        self.lbl_info1 = tk.Label(self.root, width=16, height = 1, anchor='w', text="Vol Imp: " + str(round(100*self.vi, 2)))
        self.lbl_info1.place(y = 240, x = 250)

        self.lbl_info2 = tk.Label(self.root, width=25, height = 1, anchor='w', text=('Delta: ' + str(round(self.deltaVI, 4))))
        self.lbl_info2.place(y = 260, x = 250)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Theta: " + str(round(self.thetaVI, 4)))
        self.lbl_info3.place(y = 280, x = 250)

        self.lbl_info1 = tk.Label(self.root, width=16, height = 1, anchor='w', text="Gamma: " + str(round(self.gammaVI, 4)))
        self.lbl_info1.place(y = 300, x = 250)

        self.lbl_info2 = tk.Label(self.root, width=25, height = 1, anchor='w', text=('Vega: ' + str(round(self.vegaVI, 4))))
        self.lbl_info2.place(y = 320, x = 250)

        self.lbl_info3 = tk.Label(self.root, width=25, height = 1, anchor='w', text="Rho: " + str(round(self.rhoVI, 4)))
        self.lbl_info3.place(y = 340, x = 250)



Calculadora_BS(0.1375, 30)
