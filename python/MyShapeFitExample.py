################################################################
## In principle all you have to setup is defined in this file ##
################################################################

## This configuration extends MyOneBinExample.py to use met/meff shape
## Only two systematics are considered:
##   -JES (Tree-based)
##   -Alpgen Kt scale (weight-based)
##

from configManager import configMgr
from ROOT import TMsgLevel, TMsgLogger
from ROOT import kBlack,kWhite,kGray,kRed,kPink,kMagenta,kViolet,kBlue,kAzure,kCyan,kTeal,kGreen,kSpring,kYellow,kOrange
from configWriter import TopLevelXML,Measurement,ChannelXML,Sample
from systematic import Systematic
from math import sqrt

from ROOT import gROOT
gROOT.LoadMacro("./macros/AtlasStyle.C")
import ROOT
ROOT.SetAtlasStyle()

# temporarily done here to match C++ - will be fixed in next iteration
#// define outside of class to facilite access
#enum TMsgLevel { 
    #kVERBOSE = 1, 
    #kDEBUG   = 2,
    #kINFO    = 3,
    #kWARNING = 4,
    #kERROR   = 5,
    #kFATAL   = 6,
    #kALWAYS  = 7
#};
kVERBOSE=1
kDEBUG=2
kINFO=3
kWARNING=4
kERROR=5
kFATAL=6
kALWAYS=7

configMgr.setLogLevel(1)
configMgr.writeLogMessage(kWARNING, "warning from python")

#-------------------------------
# Parameters for hypothesis test
#-------------------------------
#configMgr.doHypoTest=False
#configMgr.nTOYs=1000
configMgr.calculatorType=2
configMgr.testStatType=3
configMgr.nPoints=20


#-------------------------------------
# Now we start to build the data model
#-------------------------------------

# First define HistFactory attributes
configMgr.analysisName = "MyShapeFitExample"
configMgr.histCacheFile = "data/"+configMgr.analysisName+".root"
configMgr.outputFileName = "results/"+configMgr.analysisName+"_Output.root"

# Scaling calculated by outputLumi / inputLumi
configMgr.inputLumi = 0.001 # Luminosity of input TTree after weighting
configMgr.outputLumi = 4.713 # Luminosity required for output histograms
configMgr.setLumiUnits("fb-1")

# Set the files to read from
bgdFiles = []
if configMgr.readFromTree:
    bgdFiles.append("samples/tutorial/SusyFitterTree_OneSoftEle_BG_v3.root")
    bgdFiles.append("samples/tutorial/SusyFitterTree_OneSoftMuo_BG_v3.root")
else:
    bgdFiles = [configMgr.histCacheFile]
    pass
configMgr.setFileList(bgdFiles)

# Dictionnary of cuts for Tree->hist
configMgr.cutsDict["SR"] = "((lep1Pt < 20 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==7) || (lep1Pt < 25 && lep2Pt<10 && met>250 && mt>100 && jet1Pt>130 && jet2Pt>25 && AnalysisType==6))"


# Tuples of nominal weights without and with b-jet selection
configMgr.weights = ("genWeight","eventWeight","leptonWeight","triggerWeight","truthWptWeight","bTagWeight2Jet")
    
# QCD weights without and with b-jet selection
configMgr.weightsQCD = "qcdWeight"
configMgr.weightsQCDWithB = "qcdBWeight"

#--------------------
# List of systematics
#--------------------

# Alpgen KtScale (weight-based)
ktScaleWHighWeights = ("genWeight","eventWeight","ktfacUpWeightW","bTagWeight2Jet")
ktScaleWLowWeights = ("genWeight","eventWeight","ktfacDownWeightW","bTagWeight2Jet")
wzKtScale = Systematic("KtScaleWZ",configMgr.weights,ktScaleWHighWeights,ktScaleWLowWeights,"weight","overallSys")

ktScaleTopHighWeights = ("genWeight","eventWeight","ktfacUpWeightTop","bTagWeight2Jet")
ktScaleTopLowWeights = ("genWeight","eventWeight","ktfacDownWeightTop","bTagWeight2Jet")
#topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","overallSys")
topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","histoSys")
#topKtScale = Systematic("KtScaleTop",configMgr.weights,ktScaleTopHighWeights,ktScaleTopLowWeights,"weight","normHistoSys")

#JES (tree-based)
jes = Systematic("JES","_NoSys","_JESup","_JESdown","tree","overallSys")
configMgr.nomName = "_NoSys"

#-------------------------------------------
# List of samples and their plotting colours
#-------------------------------------------
topSample = Sample("Top",kGreen-9)
#topSample.setNormFactor("mu_Top",1.,0.,5.)
wzSample = Sample("WZ",kAzure+1)
#wzSample.setNormFactor("mu_WZ",1.,0.,5.)
dataSample = Sample("Data",kBlack)
dataSample.setData()


#**************
# Exclusion fit
#**************

#Fit config instance
exclusionFitConfig = configMgr.addTopLevelXML("Exclusion")
meas=exclusionFitConfig.addMeasurement(name="NormalMeasurement",lumi=1.0,lumiErr=0.039)
meas.addPOI("mu_SIG")

#Samples
exclusionFitConfig.addSamples([topSample,wzSample,dataSample])

# Systematics
exclusionFitConfig.getSample("Top").addSystematic(topKtScale)
exclusionFitConfig.getSample("WZ").addSystematic(wzKtScale)
exclusionFitConfig.addSystematic(jes)

#Channel
srBin = exclusionFitConfig.addChannel("met/meff2Jet",["SR"],6,0.1,0.7)
srBin.useOverflowBin=True
srBin.useUnderflowBin=True
exclusionFitConfig.setSignalChannels([srBin])

sigSample = Sample("SM_GG_onestepCC_425_385_345",kPink)
sigSample.setFileList(["samples/tutorial/SusyFitterTree_p832_GG-One-Step_soft_v1.root"])
sigSample.setNormByTheory()
sigSample.setNormFactor("mu_SIG",1.,0.,5.)                    
exclusionFitConfig.addSamples(sigSample)
exclusionFitConfig.setSignalSample(sigSample)

#2nd cloned-copy just to accomodate -l option...
exclusionFitClone = configMgr.addTopLevelXMLClone(exclusionFitConfig,"ExclusionFitClone")

