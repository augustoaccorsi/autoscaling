from datetime import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.stattools import adfuller
from pmdarima import auto_arima
from statsmodels.tsa.arima_model import ARIMA
import warnings, math, sys
from statsmodels.tsa.stattools import acf
warnings.filterwarnings("ignore")   

class Timeseries:

    def __init__(self, path):   
        data_xls = pd.read_excel('dataset\\'+path+'.xlsx', 'Sheet1', dtype=str, index_col=None)
        data_xls.to_csv('dataset\\'+path+'.csv', encoding='utf-8', index=False) 
        self._df=pd.read_csv('dataset\\'+path+'.csv', index_col='date',parse_dates=True)
        
        self._df=self._df.dropna()
        
        self._arima = None
        self._model = None
        self._model_fit = None
        self._accuracy = 0
        self._train = None
        self._test = None
        self._history = None
        self._predictions = list()
        self._error = None
        self._forecast = []
        self._path = path
        self._model_fit = None

        self._mape = 0
        self._me = 0
        self._mae = 0
        self._mpe = 0
        self._rmse = 0
        self._acf1 = 0
        self._corr = 0
        self._minmax = 0

        self._arima_order = ""

        self._error = False

    def plot(self):
        self._df.plot(figsize=(12,5))
        plt.show()

    def plot_autocorrelation(self):
        plt.subplots(figsize=(12, 5))
        autocorrelation_plot(self._df)
        plt.show()
    
    def adf_test(self): #Augmented Dickey-Fuller unit root test
        dftest = adfuller(self._df, autolag = 'AIC')
        print("1. ADF : ",dftest[0])
        if  dftest[1] < 0.05:
            print("2. P-Value : "+ str(dftest[1])+" OK")
        else:
            print("2. P-Value : ", dftest[1])
        print("3. Num Of Lags : ", dftest[2])
        print("4. Num Of Observations Used For ADF Regression and Critical Values Calculation :", dftest[3])
        print("5. Critical Values :")
        for key, val in dftest[4].items():
            print("\t",key, ": ", val)

    def get_arima_order(self, trace):
        self._arima = auto_arima(self._df, trace=trace, seasonal=True, suppress_warnings=True) 
    
    def fit_model(self):
        try:
            self._model = ARIMA(self._df, order=self._arima.get_params()['order'])
            self._arima_order = str(self._arima.get_params()['order'])
            self._model_fit = self._model.fit(disp=0)
        except:
            self._model = ARIMA(self._df, order=(5,1,0)) # try (5,1,0) to induce stationary
            self._arima_order =  "(5,1,0)"
            self._model_fit = self._model.fit(disp=0)
        
        return self._model_fit.summary()
    
    def plot_residual_errors(self):
        residuals = pd.DataFrame(self._model_fit.resid)
        residuals.plot(figsize=(12, 5))
        plt.title('ARMA Fit Residual Error Line Plot')
        plt.show()

        residuals.plot(kind='kde', figsize=(12, 5))
        plt.title('ARMA Fit Residual Error Density Plot')
        plt.show()

        return residuals.describe()

    def predict(self):
        X = self._df.values
        size = int(len(X) * 0.66)
        self._train, self._test = X[0:size], X[size : len(X)]
        self._history = [x for x in self._train]
        
        try:
            for t in range(len(self._test)):
                self.model = ARIMA(self._history, order=self._arima.get_params()['order'])
                self._arima_order = str(self._arima.get_params()['order'])
                self._model_fit = self.model.fit(disp=0)
                output = self._model_fit.forecast()
                yhat = output[0]
                self._predictions.append(yhat)
                obs = self._test[t]
                self._history.append(obs)
        except:
            self._predictions = list()
            self._history = [x for x in self._train]
            for t in range(len(self._test)):
                self.model = ARIMA(self._history, order=(5, 1, 0))  # try (5,1,0) to induce stationary
                self._arima_order =  "(5,1,0)"
                self._model_fit = self.model.fit(disp=0)
                output = self._model_fit.forecast()
                yhat = output[0]
                self._predictions.append(yhat)
                obs = self._test[t]
                self._history.append(obs)

        self.forecast_accuracy(self._predictions, self._test)

        return self

    def forecast_accuracy(self, forecast, actual):
        self._mape = np.mean(np.abs(forecast - actual)/np.abs(actual))  # MAPE
        self._me = np.mean(forecast - actual)             # ME
        self._mae = np.mean(np.abs(forecast - actual))    # MAE
        self._mpe = np.mean((forecast - actual)/actual)   # MPE
        self._rmse = np.mean((forecast - actual)**2)**.5  # RMSE
        self._corr = np.corrcoef(forecast, actual)[0,1]   # corr
        mins = np.amin(np.hstack([forecast, 
                                actual]), axis=1)
        maxs = np.amax(np.hstack([forecast, 
                                actual]), axis=1)
        self._minmax = 1 - np.mean(mins/maxs)             # minmax
        self._acf1 = acf(forecast-actual)[1]              # ACF1

        self._accuracy = 100 - self._mape
            
    def forecast(self, next):
        pred = self._model_fit.forecast(steps=next)

        for prediction in pred[0]:
            self._forecast.append(float(prediction))     

    def plot_predicition(self):
        plt.subplots(figsize=(12, 5))
        plt.plot(self._test)
        plt.plot(self._predictions, color="red")
        plt.legend(["test", "prediction"])
        plt.show()

    def print_data(self):
        print("Dataset: "+self._path)
        print("Accuracy: "+str(self._accuracy))
        print("MAE: "+str(self._mae))
        print("RMSE: "+str(self._rmse))
        #print("RMSSE: ")
        print("MAPE: "+str(self._mape))
        #print("Forecast Values: "+str(self._forecast[0]))
        print("Forecast Values: "+str(self._forecast))
       # print("ARIMA: "+self._arima_order)

    def execute(self, output, next):
        try:
            self.get_arima_order(False)
            self.fit_model()
            self.predict().forecast(next)
            if output == True:
                self.print_data()
        except:
            print("Lack of data in dataset "+self._path+", please wait for more analysis")
            self._error = True

if __name__ == '__main__':
    try:
        timeseries = Timeseries(sys.argv[1])
    except:
        timeseries = Timeseries("cpu")
    #timeseries.plot()
    #timeseries.plot_autocorrelation()
    #timeseries.adf_test()
    timeseries.get_arima_order(False)   
    timeseries.fit_model()
    #timeseries.plot_residual_errors()
    timeseries.predict().forecast(3)
    #timeseries.plot_predicition()
    timeseries.print_data()