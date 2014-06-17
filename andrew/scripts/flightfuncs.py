import numpy as np
import MySQLdb as mdb
import pandas as pd
import sklearn.feature_extraction
import sys

import load_credentials_nogit as creds
import global_vars as gv
#This file contains useful classes and functions for doing querying, encoding, and modeling of my flight data.

#Bin up delay times/cancellation. This is a class so you can instantiate it when you train your data, then pickle it with everything else, and then the encoding can be unpickled and applied later (unlike, say, a function).
class time_coder:
    def __init__(self,timebins):
        self.timebins = timebins
        self.bin_text_dict = {}
    def time_encode(self,times,cancellations):
        if self.timebins:
            coded_array = np.zeros(len(times),dtype=np.int)
            self.bin_text_dict[0] = '<{0:d}'.format(self.timebins[0])
            currcode = 1
            for i in range(1,len(self.timebins)):
                coded_array[(times >= self.timebins[i-1]) & (times < self.timebins[i])] = currcode
                self.bin_text_dict[currcode] = '{0:d}-{1:d}'.format(self.timebins[i-1],self.timebins[i])
                currcode += 1
            coded_array[(times >= self.timebins[-1])] = currcode
            self.bin_text_dict[currcode] = '>={0:d}'.format(self.timebins[-1])
            currcode += 1
            coded_array[(cancellations > 1.e-5)] = currcode
            self.bin_text_dict[currcode] = 'Cancelled'
            return coded_array.astype(np.str)
        else:
            raise ValueError("time_coder.timebins is empty!")

#Prepping a dataframe of predictors, including doing (hopefully) fast one-hot encoding of categorical variables. Like time_coder, this is a class and not a function to improve portability between training and actually using the model.
class predictor_coder:
    def __init__(self):
        self.continuous_predictors = None
        self.discrete_predictors = None
        self.discrete_predictor_mapping = None

    #Code the training predictors:
    def train(self,data,continuous_predictors,discrete_predictors):
        #Make sure the predictors are in the data:
        self.check_predictors(data,continuous_predictors)
        self.check_predictors(data,discrete_predictors)

        #Assuming that's all kosher, save the predictors:
        self.continuous_predictors = continuous_predictors
        self.discrete_predictors = discrete_predictors
        self.discrete_predictor_mapping = [None]*len(discrete_predictors)

        #Code up the data:
        coded_arr = self.code_data(data)
        return coded_arr

    #Code up the predictors:
    def code_data(self,data):
        if self.continuous_predictors == None or self.discrete_predictors == None or self.discrete_predictor_mapping == None:
            raise TypeError("Must train predictor before you can code on it!")
        
        #Prep the 2D array:
        coded_arr = np.zeros((1,data.shape[0]))

        #First do any continuous predictors (easy):
        if self.continuous_predictors:
            coded_arr = np.vstack((coded_arr,data[self.continuous_predictors].values.T))

        #Next, do the discrete predictors (harder):
        for i, pred in enumerate(self.discrete_predictors):
            stacked_codes = self.one_hot_code(data[pred].values,i)
            coded_arr = np.vstack((coded_arr,stacked_codes))

        return coded_arr[1:,:].T

    #One-hot coding of discrete predictors:
    def one_hot_code(self,values,prednum):
        if self.discrete_predictor_mapping[prednum] == None:
            unique_values = np.unique(values)
            self.discrete_predictor_mapping[prednum] = dict(zip(unique_values,range(len(unique_values))))

        codes = [self.discrete_predictor_mapping[prednum][key] for key in values]
        code_arr = np.zeros((len(self.discrete_predictor_mapping[prednum].keys()),len(values)))
        code_arr[codes,range(len(values))] = 1.

        return code_arr
    
    #Raise an exception if the predictors aren't in the dataframe:
    def check_predictors(self,data,predictors):
        datacols = data.columns.values
        if np.sum(np.in1d(predictors,datacols)) < len(predictors):
            raise ValueError("Not all predictors in dataframe!")

def make_model_pickle_filename(tablename,predlist,dir_structure="../saved_models/"):
    return "{dir}{table}_{preds}.pkl".format(dir=dir_structure,table=tablename,preds='-'.join(np.sort(predlist)).replace('(','~').replace(')','~'))

#A function to take in a date, time, and predictors and determine the proper model to use:
def get_model_filename(datetime_obj,predictorlist,tableprefix='flightdelays',dir_structure="../saved_models/"):
    #Convert the time into the proper format:
    int_time = datetime_obj.hour*100 + datetime_obj.minute
    time_name = None
    for key in gv.hours.keys():
        if int_time >= gv.hours[key][0] and int_time < gv.hours[key][1]:
            time_name = key
            break
    if time_name == None:
        raise ValueError("get_model_filename: Time {0:d} outside of allowed range!".format(int_time))

    #Convert the month into the proper format:
    month_name = None
    for key in gv.months.keys():
        if datetime_obj.month == gv.months[key]:
            month_name = key
            break
    if month_name == None:
        raise ValueError("get_model_filename: Month {0:d} outside of allowed range!".format(datetime_obj.month))

    #Get the required filename:
    filename = make_model_pickle_filename(tableprefix+"_"+month_name+"_"+time_name,predictorlist,dir_structure=dir_structure)
    return filename
    #print int_time,time_name,month_name
    #print filename
    
    
#A cross-validation estimator based on the probability of the label being the correct one, normal goodness-of-model measurements like accuracy aren't relevant here:
def pdf_scoring(estimator, X, y):
    integer_y = y.astype(np.int16)
    probs = estimator.predict_proba(X)[range(len(integer_y)),integer_y]
    return np.sum(probs**2)

#Get selected columns and put them into a Pandas Dataframe:
def query_into_pd(con,table,columnlist,subset=None,randomize=False):
    if columnlist:
        syntax = "Select {cols} from {table}".format(table=table,cols=', '.format(table=table).join(columnlist))
        df = pd.io.sql.read_sql(syntax,con)
        try:
            if int(subset) > 0:
                if int(subset) >= len(df):
                    print "Warning: Requested subset larger than queried data. Using full dataset..."
                else:
                    df = df.ix[np.random.choice(np.arange(len(df)),replace=False,size=int(subset))]
        except TypeError:
            pass
        if randomize:
            indices = df.index.values.copy()
            np.random.shuffle(indices)
            df.reindex(indices)
        return df
    else:
        raise IndexError("No columns to be selected!")
        

if __name__ == "__main__":
    #Testing the functions as I go:
    con = mdb.connect(host=creds.host,user=creds.user,db=creds.database,passwd=creds.password,local_infile=1)
    df = query_into_pd(con,'flightdelays_mar_early',['origin','dest','uniquecarrier','arrdelay','cancelled','diverted'],subset=None)
    print df.shape
