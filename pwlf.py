# -- coding: utf-8 -- 
#   import libraris
import numpy as np
from scipy.optimize import differential_evolution

#   version 0.0.1

#   piecewise linerar fit library
class piecewise_lin_fit:
    
    #   Initiate the libary with the supplied x and y data
    #   where y(x). For now x and y should be 1D numpy arrays.
    def __init__(self, x, y):
        #   you must supply the x and y data of which you'll be fitting 
        #   a continous piecewise linear model to where y(x)
        
        #   sort the data from least x to max x
        orderArg = np.argsort(x)
        self.xData = x[orderArg]
        self.yData = y[orderArg]
        
        #   calculate the number of data points
        self.nData = len(x)
    
        
    def fitWithBreaks(self, breaks):
    #   define a function which fits the piecewise linear function
    #   for specified break point locations
    #
    #   The function minimizes the sum of the square of the residuals for the
    #    pair of x,y data points   
    #   
    #   This is a port of 4-May-2004 Nikolai Golovchenko MATLAB code
    #   see http://golovchenko.org/docs/ContinuousPiecewiseLinearFit.pdf
    #   
    #   Alternatively see https://www.mathworks.com/matlabcentral/fileexchange/40913-piecewise-linear-least-square-fit
    #   
    #   Input:   
    #   provide the location of the end points of the breaks for each line segment
    #   
    #   Example: if your x data exists from 0 <= x <= 1 and you want three
    #   piecewise linear lines, an accpetable breaks would look like
    #   breaks = [0.0, 0.3, 0.6, 1.0]
    #   
    #   Ouput:
    #   The function returns the sum of the square of the residuals
    #   
    #   To get the parameters of the fit look for 
    #   self.paramters
    #
    #   remember that the parameters that result are part of the continous function
    #   such that:
    #   parameters = f(breaks)
        self.fitBreaks = breaks
        numberOfParameters = len(breaks)
        numberOfSegments = numberOfParameters - 1
        
        self.numberOfParameters = numberOfParameters
        self.numberOfSegments = numberOfSegments
        
        sepDataX, sepDataY = self.seperateData(breaks)
        
        #   compute matricies corresponding to the system of equations
        A = np.zeros([numberOfParameters, numberOfParameters])
        B = np.zeros(numberOfParameters)
        for i in range(0,numberOfParameters):
            if i != 0:
                #   first sum
                A[i,i-1] = A[i,i-1] - sum((sepDataX[i-1] - breaks[i-1]) * (sepDataX[i-1] - breaks[i])) / ((breaks[i] - breaks[i-1]) ** 2)
                A[i,i] = A[i,i] + sum((sepDataX[i-1] - breaks[i-1]) ** 2) / ((breaks[i] - breaks[i-1]) ** 2)
                B[i] = B[i] + (sum(sepDataX[i-1] * sepDataY[i-1]) - breaks[i-1] * sum(sepDataY[i-1])) / (breaks[i] - breaks[i-1])
        
            if i != numberOfParameters - 1:
                #   second sum
                A[i,i] = A[i,i] + sum(((sepDataX[i] - breaks[i+1]) ** 2)) / ((breaks[i+1] - breaks[i]) ** 2)
                A[i,i+1] = A[i,i+1] - sum((sepDataX[i] - breaks[i]) * (sepDataX[i] - breaks[i+1])) / ((breaks[i+1] - breaks[i]) ** 2)
                B[i] = B[i] + (-sum(sepDataX[i] * sepDataY[i]) + breaks[i+1] * sum(sepDataY[i])) / (breaks[i+1] - breaks[i])
        
        p = np.linalg.solve(A,B)

        yHat = []        
        for i,j in enumerate(sepDataX):
            m = (p[i+1] - p[i])/(breaks[i+1]-breaks[i])
            yHat.append(m*(j-breaks[i]) + p[i])
        yHat = np.concatenate(yHat)
        
        #   calculate the sum of the square of residuals
        e = self.yData-yHat
        SSr = np.dot(e.T,e)


        self.fitParameters = p

        return(SSr)
    
    def seperateData(self, breaks):
    #   a function that seperates the data based on the breaks
        
        numberOfParameters = len(breaks)
        numberOfSegments = numberOfParameters - 1
        
        self.numberOfParameters = numberOfParameters
        self.numberOfSegments = numberOfSegments
        
        #   Seperate Data into Segments
        sepDataX = [[] for i in range(self.numberOfSegments)]
        sepDataY = [[] for i in range(self.numberOfSegments)]
        
        for i in range(0, self.numberOfSegments):
            dataX = []
            dataY = []
            aTest = self.xData >= breaks[i]
            dataX = np.extract(aTest, self.xData)
            dataY = np.extract(aTest, self.yData)
            bTest = dataX <= breaks[i+1]
            dataX = np.extract(bTest, dataX)
            dataY = np.extract(bTest, dataY)
            sepDataX[i] = np.array(dataX)
            sepDataY[i] = np.array(dataY)  
        return(sepDataX, sepDataY)
    
    def seperateDataX(self, breaks, x):
    #   a function that seperates the data based on the breaks for given x
        
        numberOfParameters = len(breaks)
        numberOfSegments = numberOfParameters - 1
        
        self.numberOfParameters = numberOfParameters
        self.numberOfSegments = numberOfSegments
        
        #   Seperate Data into Segments
        sepDataX = [[] for i in range(self.numberOfSegments)]
        
        for i in range(0, self.numberOfSegments):
            dataX = []
            aTest = x >= breaks[i]
            dataX = np.extract(aTest, x)
            bTest = dataX <= breaks[i+1]
            dataX = np.extract(bTest, dataX)
            sepDataX[i] = np.array(dataX)
        return(sepDataX)
         
    def predict(self, x, *args):#breaks, p):
        #   a function that predicts based on the supplied x values
        #    you can manully supply break point and determined p
        #   yHat = predict(x)
        #   or yHat = predict(x, p, breaks)
        if len(args) == 2:
            p = args[0]
            breaks = args[1]
        else:
            p = self.fitParameters
            breaks = self.fitBreaks
        
        #   seperate the data by x on breaks
        sepDataX = self.seperateDataX(breaks,x)
        yHat = []
        for i,j in enumerate(sepDataX):
            m = (p[i+1] - p[i])/(breaks[i+1]-breaks[i])
            yHat.append(m*(j-breaks[i]) + p[i])
        yHat = np.concatenate(yHat)
        return(yHat)
        
    def fitWithBreaksOpt(self, var):
        #   same as self.fitWithBreaks, excpet this one is tuned to be used with
        #   the optimization algorithim
        var = np.sort(var)
        if np.isclose(var[0],var[1]) == True:
            var[1] += 0.00001
        breaks = np.zeros(len(var)+2)
        breaks[1:-1] = var.copy()
        breaks[0] = self.break0
        breaks[-1] = self.breakN

        sepDataX, sepDataY = self.seperateData(breaks)
        
        numberOfParameters = self.numberOfParameters

        #   compute matricies corresponding to the system of equations
        A = np.zeros([numberOfParameters, numberOfParameters])
        B = np.zeros(numberOfParameters)
        for i in range(0,numberOfParameters):
            if i != 0:
                #   first sum
                A[i,i-1] = A[i,i-1] - sum((sepDataX[i-1] - breaks[i-1]) * (sepDataX[i-1] - breaks[i])) / ((breaks[i] - breaks[i-1]) ** 2)
                A[i,i] = A[i,i] + sum((sepDataX[i-1] - breaks[i-1]) ** 2) / ((breaks[i] - breaks[i-1]) ** 2)
                B[i] = B[i] + (sum(sepDataX[i-1] * sepDataY[i-1]) - breaks[i-1] * sum(sepDataY[i-1])) / (breaks[i] - breaks[i-1])
        
            if i != numberOfParameters - 1:
                #   second sum
                A[i,i] = A[i,i] + sum(((sepDataX[i] - breaks[i+1]) ** 2)) / ((breaks[i+1] - breaks[i]) ** 2)
                A[i,i+1] = A[i,i+1] - sum((sepDataX[i] - breaks[i]) * (sepDataX[i] - breaks[i+1])) / ((breaks[i+1] - breaks[i]) ** 2)
                B[i] = B[i] + (-sum(sepDataX[i] * sepDataY[i]) + breaks[i+1] * sum(sepDataY[i])) / (breaks[i+1] - breaks[i])

        #   calc determinant of A, then pass infinity if the case
        if np.linalg.det(A) == 0:
            SSr = np.inf
        else:
            p = np.linalg.solve(A,B)
    
            yHat = []        
            for i,j in enumerate(sepDataX):
                m = (p[i+1] - p[i])/(breaks[i+1]-breaks[i])
                yHat.append(m*(j-breaks[i]) + p[i])
            yHat = np.concatenate(yHat)
    
            
            #   calculate the sum of the square of residuals
            e = self.yData-yHat
            SSr = np.dot(e.T,e)
        return(SSr)
    
    def fit(self, numberOfSegments, **kwargs):
        #   a function which uses differntial evolution to finds the optimum
        #   location of break points for a given number of line segments by 
        #   minimizing the sum of the square of the errors
        #   
        #   input:
        #   the number of line segments that you want to find 
        #   the optimum break points for
        #   ex:
        #   breaks = fit(3)
        #
        #   output:
        #   returns the break points of the optimal piecewise contionus lines
        
        self.numberOfSegments = int(numberOfSegments)
        self.numberOfParameters = self.numberOfSegments+1

        #self.fitBreaks = self.numberOfSegments+1
        
        #   set the first and last break x values to be the min and max of x
        self.break0 = np.min(self.xData)
        self.breakN = np.max(self.xData)
        
        #   calculate the number of variables I have to solve for
        self.nVar = self.numberOfSegments - 1
        
        #   initaite the bounds of the optimization
        bounds = np.zeros([self.nVar, 2])
        bounds[:,0] = self.break0
        bounds[:,1] = self.breakN
        
        if len(kwargs) == 0:
            res = differential_evolution(self.fitWithBreaksOpt, bounds, strategy='best1bin',
                    maxiter=1000, popsize=50, tol=1e-3, mutation=(0.5, 1), 
                    recombination=0.7, seed=None, callback=None, disp=False, 
                    polish=True, init='latinhypercube', atol=1e-4)
        else:
            res = differential_evolution(self.fitWithBreaksOpt, bounds, **kwargs)
        print(res)
        
        self.SSr = res.fun
        
        var = np.sort(res.x)
        if np.isclose(var[0],var[1]) == True:
            var[1] += 0.00001
        breaks = np.zeros(len(var)+2)
        breaks[1:-1] = var.copy()
        breaks[0] = self.break0
        breaks[-1] = self.breakN
        self.fitBreaks = breaks
        #   assign p
        self.fitWithBreaks(self.fitBreaks)
        
        return(self.fitBreaks)
        
    def useCustomOpt(self,numberOfSegments):
        #   provide the number of line segments you want to use with your
        #   custom optimization routine
        #
        #   then optimize fitWithBreaksOpt(var) where var is a 1D array 
        #   containing the x locations of your variables
        #   var has length numberOfSegments - 1, because the two break points
        #   are always defined (1. the min of x, 2. the max of x)
        #
        #   fitWithBreaksOpt(var) will return the sum of the square of the 
        #   residuals which you'll want to minimize with your optimization 
        #   routine
        
        self.numberOfSegments = int(numberOfSegments)
        self.numberOfParameters = self.numberOfSegments+1

        #self.fitBreaks = self.numberOfSegments+1
        
        #   set the first and last break x values to be the min and max of x
        self.break0 = np.min(self.xData)
        self.breakN = np.max(self.xData)
        
        #   calculate the number of variables I have to solve for
        self.nVar = self.numberOfSegments - 1

    def findBreaks(self,x,y):
        #   return breaks in time series y
        #   step 1、Polynomial fitting
        #   step 2、seeking roots

        breaks = []

        #   determine n in Polynomial fitting
        n = self.findPolyN(x,y)

        #    fit the Polynomial 
        z1 = np.polyfit(x, y,n)

        #   Form a function
        f1 = np.poly1d(z1)

        #   seeking roots
        f_pi= np.polyder(f1) 
        root  = np.roots(f_pi) 

        #   store the breaks
        k = 0
        while k < len(root):
            if(root[k]>min(x) and root[k] <max(x)):
                breaks.append(root[k])
            k = k +1    
        return sorted(breaks)

    def findPolyN(self,x,y):
        #   determine n in Polynomial fitting
        #   find the first one who makes the value of Least Squares Method less than 10  
        #   you can modify the parameter(10) to meet your requirement
        cursum = 0
        presum = 0
        n = 1
        while  1:
            z1 = np.polyfit(x, y,n)
            f1 = np.poly1d(z1)
            yvals=f1(x)
            i = 0
            sum = 0           
            for i in range(0,len(y)):
                sum =0.5*( sum +(y[i]-yvals[i])**2)
                i = i +1
            presum = cursum
            cursum =sum     
            if(cursum < 10 and presum>=cursum):
                break
            n = n + 1
        return n