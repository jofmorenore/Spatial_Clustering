from GeometryComputation import *
from ShapeReader import ShapeReader
from math import log1p
from GurobiSolver import gbSolve

class GLLR:
    
    def __init__(self, shpFilePath, idf, af, ef, rf):
        sr=ShapeReader(shpFilePath)
        sr.readFileWithID(idf, af, ef, rf)
        self.geoDict=produceGeo(sr.shpDict, "Polygon")
        self.actualDict=sr.fdDict1
        self.expectDict=sr.fdDict2
        self.relaRiskDict=sr.fdDict3
        
        self.adjRookDict={}
        self.adjQueenDict={}

                
    def createAdjSets(self):
        geoList = []
        keyList = sorted(self.geoDict.keys())
        for k in keyList:
            geoList.append(self.geoDict[k])
            self.adjRookDict[k]=[]
            self.adjQueenDict[k]=[]
            
        totalLen=len(geoList)
        
        for i, geo in enumerate(geoList[:-1]):    
            for j in range(i+1, totalLen):                                   
                inter=geo.intersection(geoList[j])
                if inter:                  
                    linkLen=inter.length
                    if linkLen > 0:
                        self.adjQueenDict[keyList[i]].append(keyList[j])
                        self.adjQueenDict[keyList[j]].append(keyList[i])
                        self.adjRookDict[keyList[j]].append(keyList[i])
                        self.adjRookDict[keyList[i]].append(keyList[j])
                    if linkLen == 0:
                        self.adjQueenDict[keyList[i]].append(keyList[j])
                        self.adjQueenDict[keyList[j]].append(keyList[i])       

    def generateGLLRModel_case(self, totalEvents, clusterCases, clusterRegions, outputFilePath):   
        adjDict = self.adjQueenDict
        outputFile=open(outputFilePath, 'w')
        outputFile.write('Maximize')
        outputFile.write('\n')
        outputFile.write(' uz' )
        
        outputFile.write('\n')
        outputFile.write('Subject To')
        outputFile.write('\n')
        
        keyList=self.geoDict.keys()
        keyList.sort()
        XVarList=[]
        outputFile.write(' OB: -1 uz')
        for k in keyList:
            XVarList.append('x%d' %(k,))
            acValue = self.actualDict[k]
            exValue = self.expectDict[k]
            outputFile.write(' + %f x%d' %(acValue-exValue, k))
        outputFile.write(' = 0')
        outputFile.write('\n')
        
        outputFile.write(' CU: uz < %d\n' %(clusterCases,))           
        
        outputFile.write(' CA: ')           
        for ink, k in enumerate(keyList):
            if ink == (len(keyList)-1):
                outputFile.write('%d x%d = %d' %(self.actualDict[k], k, clusterCases))
            else:
                outputFile.write('%d x%d + ' %(self.actualDict[k], k))
        outputFile.write('\n')
            
        j=1       
        for k in keyList:
            lenAdj = len(adjDict[k])
            if lenAdj == 0:
                continue
            outputFile.write(' FB%d: ' %(j,))
            for indAdj, adj in enumerate(adjDict[k]):
                if indAdj == (lenAdj-1):                    
                    outputFile.write('y%dj%d - y%dj%d - x%d + %d v%d >= 0' %(k, adj, adj, k, k, len(keyList), k))
                else:
                    outputFile.write('y%dj%d - y%dj%d + ' %(k, adj, adj, k))
            j = j+1
            outputFile.write('\n')
            
        VVarList = []
        outputFile.write(' SK: ')
        for ink, k in enumerate(keyList):           
            if ink == (len(keyList)-1):
                outputFile.write('v%d = %d' %(k, clusterRegions))
                VVarList.append('v%d' %(k,))
            else:
                outputFile.write('v%d + ' %(k,))
                VVarList.append('v%d' %(k,))
        outputFile.write('\n')

        j=1        
        for k in keyList:
            lenAdj = len(adjDict[k])
            if lenAdj == 0:
                continue
            outputFile.write(' FS%d: ' %(j,))
            for indAdj, adj in enumerate(adjDict[k]):
                if indAdj == (lenAdj-1):                    
                    outputFile.write('y%dj%d - %d x%d <= 0' %(k, adj, len(keyList)-1, k))
                else:
                    outputFile.write('y%dj%d + ' %(k, adj))
            j = j+1
            outputFile.write('\n')

        j=1        
        for k in keyList:
            outputFile.write(' SL%d: x%d - v%d >= 0\n' %(j, k, k))
            j = j+1
            outputFile.write('\n')
            
        outputFile.write('\n')        
        outputFile.write('Binary')
        outputFile.write('\n')        

        varList = []
        varList.extend(XVarList)
        varList.extend(VVarList)
        for i in range(len(varList)):
            outputFile.write(' %s' %(varList[i], ))
            if i%11==0:
                outputFile.write('\n')
                outputFile.write(' ')
                
        outputFile.write('\n')    
        outputFile.write('End') 
        
