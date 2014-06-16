### General Paths ####
from pypaths import *

### QUANDL Stock date range info
#start_date = '2000-01-01'
end_date = '2005-12-31'
start_date = '2004-01-01'
#end_date = '2010-12-31'
authtoken="ZwZp5EomA34QgSDRezss" #this is optional

host = 'localhost'
user = 'incubator'
db = 'Commodities'

to_use = ['oil','natural_gas', 'corn', 'wheat']#,'gold','silver']


#Quandl info
stockpath = 'quandl'

indicators = { 'gold':'CHRIS/CME_GC1',
               'silver':'CHRIS/CME_SI1',
               'oil':'CHRIS/CME_CL1',
               'natural_gas':'CHRIS/CME_NG1',
               'corn':'CHRIS/CME_C1',
               'wheat':'CHRIS/CME_W1',
               'rice':'OFDP/FUTURE_RR1'
               }


baskets = {'gold':'metal',
           'silver':'metal',
           'oil':'energy',
           'natural_gas':'energy',
           'corn':'food',
           'wheat':'food',
           'rice':'food'
           }

end_months = {'wheat':[3,5,7,9,12],
              'corn': [3,5,7,9,12],
              'oil':  range(1,13),
              'natural_gas': range(1,13)
    }




##### SQL INFO  ######

sql_info = {'usr':'incubator',
            'pwd':'',
            'dba':'Commodities'
            }

