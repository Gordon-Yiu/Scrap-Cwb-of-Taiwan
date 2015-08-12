# -*- coding: utf-8 -*-
#ScrapCwbToGetTwWeatherListV1.1.2
#Web Scrapping Demo gordon.yiu@gmail.com
#You can use freely without boundary.
#

'''
ScrapCwbToGetTwWeatherListV1.1.2
scrap cwb.gov to get weather information

revision 0.1.0:
keep to polish with new learning.


revision 1.1.2
add a kml parser to automatically build the station information from:
http://www.cwb.gov.tw/wwwgis/kml/cwbobs.kml
change the input name to

'''

import sys
from bs4 import BeautifulSoup
from urllib2 import urlopen
#from time import sleep # be nice
from time import time,strptime,mktime,ctime


from pykml import parser

'''
A simple code to explain how I did it.
In the begining, it is just very simple trial and erro with a simple wish:
I want to get the temperature of my home village.
But latter on, I have to deal with many other things. Therefore I hope to provide a simple code
so that you can trace it easily. However this is not a good example. It is only used to
explain to you the important yet simple technique. Many input parse and error handlin 
are not included.
try to get temperature of this http://www.cwb.gov.tw/V7/observe/24real/Data/46708.htm
'''
#=====Start of simple code============
def getYilanTemperatureNow_simple():    
    html = urlopen('http://www.cwb.gov.tw/V7/observe/24real/Data/46706.htm').read() #<=change back!
    #use beautiful soup to parse the returned html by lxml,
    #if you have problem here, try "pip install beautifulSoup 4" and "pip install lxml"
    Soup_A=BeautifulSoup(html, "lxml")
    trList=Soup_A.findAll('tr') #break it,
    #You can un-comment the following line to check what yout get
    #print trList
    #You can un-comment the following line to check what yout get,check what findAll do for you.
    #print trList[1] # Yilan Temperature is here
    tdList=trList[1].findAll('td')
    #You can un-comment the following line to check what yout get,check what findAll do for you.
    #print tdList
    #You can un-comment the following line to check what yout get
    #print tdList[0]
    #You can un-comment the following line to check what yout get
    #print tdList[0].text
    return float(tdList[0].text)
    #And you can get the temperature, how simple? Only 5 lines of real code.
    
#=====End of simple code=============
'''
Loation and website dictionary for getting data.
These code name: 46708 for Yilan, C0C48 for Taoyuan seems to be coded by cwb....
'''
cwbPrefix='http://www.cwb.gov.tw/V7/observe/24real/Data/'


def buildCwbStaticStationDict():
    
    url = 'http://www.cwb.gov.tw/wwwgis/kml/cwbobs.kml'
    #url = 'http://code.google.com/apis/kml/documentation/KML_Samples.kml'

    fileobject = urlopen(url)
    root = parser.parse(fileobject).getroot()
    cwbStaticStationDict={}

    for i in range(100):
        try:
            k=root.Document.Placemark[i]
            stationName=k.name.text[0:len(k.name.text)-9]
            stationNumber=k.name.text[-5:]
            longitude=float(k.LookAt.longitude.text)
            latitude=float(k.LookAt.latitude.text)
            altitude=float(k.LookAt.altitude.text)
            #print stationName,stationNumber,longitude,latitude,altitude
            cwbStaticStationDict[stationName.encode('utf-8')]=[stationNumber,longitude,latitude,altitude]
            
        except IndexError:
            pass
            #print i, 'index out of range'
    #check if dic is OK        
    #print cwbStaticStationDict['金門'], len(cwbStaticStationDict)
    return(cwbStaticStationDict)



class cwbWeatherList:
    '''
    class cwbWeatherList with location, date list, time list, temperature list.....
    '''
    def __init__(self,inputLocation="YiLan"):
        self.location=inputLocation
        self.statusOK=False
        self.recordLength=0
        self.nowTemperature=18.8 #The best temperature for running, and veg and rose :-)
        self.nowEpoTime=0.0 #time 0 of epotime
        self.nowRH=88 #88% :-)
        self.nowAccuRain=8.88 #8.88mm :-)
        self.nowWeatherCondition=u'晴天' #晴天 :-)
        self.date=[]
        self.time=[]
        self.epoTime=[]
        self.temperature=[]
        self.windStrength=[]
        self.windDirection=[]
        self.RH=[]
        self.accuRain=[]
        self.weatherCondition=[]
        #print 'init==>>generate a cwbWeatherList...'
 
    def append(self,date,time,temperature,windDirection,windStrength,RH,accuRain,weatherCondition):
        '''
        append a new element to cwbWeatherList and update recordlength, nowtemp, nowtime.
        
        '''
        self.date.append(date)
        self.time.append(time)
        self.temperature.append(temperature)
        tempTime=int(mktime(strptime('2015 ' +date+' '+time,"%Y %m/%d %H:%M")))
        self.epoTime.append(tempTime)
        self.recordLength=len(self.date)
        self.windDirection.append(windDirection)
        self.windStrength.append(windStrength)
        self.RH.append(RH)
        self.accuRain.append(accuRain)
        self.weatherCondition.append(weatherCondition)
        #parse all record to see if this one is the latest one. If yes update nowTemp and nowEpoTime
        #normally first one is the most updated one, but who knows. They might change it. Since it will
        #enter the if loop one times, no much waste of time.
        for i in range(self.recordLength):
            if self.nowEpoTime<self.epoTime[i]:  #New one--->updated
                self.nowEpoTime=self.epoTime[i]
                self.nowTemperature=self.temperature[i]
                self.nowRH=self.RH[i]
                self.nowAccuRain=self.accuRain[i]
                self.nowWeatherCondition=self.weatherCondition[i]
                #print 'update now status', self.nowEpoTime, self.nowTemperature
        
        #print 'append==>>add a new list in cwbWeatherList... and update nowTemp and nowEpoTime'
        #print 'End of Append', self.nowEpoTime, self.nowTemperature
        

    
def make_soup(url):
    '''open the website in url and returen a structured lxml 
    '''
    html = urlopen(url).read()
    return BeautifulSoup(html, "lxml")    

    
def getTemperatureList(TaiwanLocation,StationDict):
    '''
    open the base url and get the temperature of whole list
    return a object "cwbTemperatureList"
    '''
    ### check if dict is here:
    #print StationDict['金門']
    #print StationDict[TaiwanLocation.encode('utf-8')]
    
    
    
    try:
        
        #print StationDict[TaiwanLocation.encode('utf-8')][0]
        
        TaiwanLocationWeather=cwbWeatherList(TaiwanLocation) #build a class instance of cwbWeatherList
        
        
        #get url with right station number and go get it
        #really confused here
        aaa=TaiwanLocation###.encode('utf-8')  #!!!!! encode is needed for key index 
        #print StationDict[aaa][0]
        url=cwbPrefix+StationDict[aaa][0]+'.htm'
        soup=make_soup(url)
        trList=soup.findAll('tr')
        
    

        #for debug purpose. if there is anything wrong, un-comments following line and check the string
        #print trList[1]   #<==work here
        for i in range(0,len(trList)):
            if i!=0:
            
                TmpList_td=trList[i].findAll('td')
                #for debug purpose. if there is anything wrong, un-comments following line and check the string
                #if i ==1: print TmpList_td
        
                try: #sometime they put '-' here if temperature not available, we have to deal with it
                    temp=float(TmpList_td[0].text)
                except ValueError,IndexError: #if not a float
                    temp=None
                    TaiwanLocationWeather.statusOK=False
                    break
    
                try: #some time data is not available
                    windD=TmpList_td[3].text
                    windS=TmpList_td[4].text
                    RH=TmpList_td[7].text  
                    accuRain=TmpList_td[9].text
                    weatherCondition=TmpList_td[2].text
                    TmpList_th=trList[i].findAll('th')
                    date=TmpList_th[0].text[:5]
                    time=TmpList_th[0].text[-5:]
                
                    TaiwanLocationWeather.append(date,time,temp,windD,windS,RH,accuRain,weatherCondition)
                    TaiwanLocationWeather.statusOK=True
                except IndexError:
                    TaiwanLocationWeather.statusOK=False
                    break
        return(TaiwanLocationWeather)
    
    except KeyError:
        TaiwanLocationWeather=cwbWeatherList('invalid') #build a class instance of cwbWeatherList
        TaiwanLocationWeather.statusOK=False
        return(TaiwanLocationWeather)
    

#example code to use and to trace. You will be surprised how simple it is. :-)
if __name__=="__main__":
    print '='*80
    print getYilanTemperatureNow_simple()



#example code to use, do not try to trace, brain killing :-()

if __name__=="__main__":
    if len(sys.argv)==2:
        location=sys.argv[1]
    else:
        location=u'蘇澳'
    #print location, sys.argv
    StationDict=buildCwbStaticStationDict()
    #check if CwbStaticStationDict is built!
    #print StationDict.keys()[0]
    a=getTemperatureList(TaiwanLocation=location,StationDict=StationDict)
    
    print '='*80
    print a.location, a.recordLength
    
    if a.statusOK:
        print a.date[0],a.date[-1]
        print a.time[0],a.time[-1]
        print a.epoTime[0],a.epoTime[-1]
        print a.temperature[0],a.temperature[-1]
        print a.windDirection[0].encode('utf-8'),a.windDirection[-1].encode('utf-8')
        print a.windStrength[0].encode('utf-8'),a.windStrength[-1].encode('utf-8')
        print a.RH[0],a.RH[-1]
        print a.accuRain[0],a.accuRain[-1],a.weatherCondition[0],a.weatherCondition[-1]
        print a.nowTemperature, a.nowEpoTime, ctime(a.nowEpoTime)
        print a.nowRH, a.nowAccuRain,a.nowWeatherCondition
    else:
        if a.location=='invalid':
            print "invalid location. I can not resolve. @.@"
        else:
            print '''I can't get data from cwb.'''
            print 'please visit: '+ cwbPrefix+dictLocationWebsite[a.location]+'.htm for details.'
    print '='*80
    
    