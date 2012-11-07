#!/usr/bin/env python
from ROOT import gROOT,gSystem,gDirectory,RooAbsData,RooRandom,RooWorkspace
gSystem.Load("libSusyFitter.so")
from ROOT import ConfigMgr
gROOT.Reset()
from logger import Logger

from logger import Logger
log = Logger('HistFitter')


def enum(typename, field_names):
    "Create a new enumeration type"

    if isinstance(field_names, str):
        field_names = field_names.replace(',', ' ').split()
    d = dict((reversed(nv) for nv in enumerate(field_names)), __slots__ = ())
    return type(typename, (object,), d)()


def GenerateFitAndPlotCPP(fc, drawBeforeAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood):
    from ROOT import Util
    
    log.debug("GenerateFitAndPlotCPP: drawBeforeAfterFit %s " % drawBeforeAfterFit) 
    log.debug("GenerateFitAndPlotCPP: drawCorrelationMatrix %s " % drawCorrelationMatrix) 
    log.debug("GenerateFitAndPlotCPP: drawSeparateComponents %s " % drawSeparateComponents)
    log.debug("GenerateFitAndPlotCPP: drawLogLikelihood %s " % drawLogLikelihood)

    #    from configManager import configMgr
    Util.GenerateFitAndPlot(fc.name, drawBeforeAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood)

def GenerateFitAndPlot(fc, drawBeforeAfterFit):
    from configManager import configMgr

    from ROOT import Util
    from ROOT import RooExpandedFitResult
    log.info("\n***GenerateFitAndPlot for TopLevelXML %s***\n" % fc.name)

    w = Util.GetWorkspaceFromFile(fc.wsFileName, "combined")
    Util.SaveInitialSnapshot(w)
    #   Util.ReadWorkspace(w, fc.wsFileName,"combined")

    plotChannels = ""
    for reg in fc.validationChannels:
        if len(plotChannels) > 0:
            plotChannels += ","
            pass
        plotChannels += reg
    plotChannels = "ALL"

    fitChannels = ""
    for reg in fc.bkgConstrainChannels:
        if len(fitChannels) > 0:
            fitChannels += ","
            pass
        fitChannels += reg
        pass

    fitChannelsCR = fitChannels
    for reg in fc.signalChannels:
        if len(fitChannels) > 0:
            fitChannels += ","
            pass
        fitChannels += reg
    #fitChannels = "ALL"

    #hack to be fixed at HistFactory level (check again with ROOT 5.34)
    lumiConst = True
    if fc.signalSample and not fc.hasDiscovery:
        lumiConst = False

    # fit toy MC if specified. When left None, data is fit by default
    toyMC = None
    if configMgr.toySeedSet and not configMgr.useAsimovSet:
        # generate a toy dataset
        log.info("generating toy MC set for fitting and plotting." \
              " Seed = %i" % configMgr.toySeed)
        toyMC = Util.GetToyMC()   # this generates one toy dataset
        pass
    elif configMgr.useAsimovSet and not configMgr.toySeedSet:
        log.info("using Asimov set for fitting and plotting.")
        toyMC = Util.GetAsimovSet(w)  # this returns the asimov set
        pass
    else:
        log.info("using data for fitting and plotting.")

    # set Errors of all parameters to 'natural' values before plotting/fitting
    Util.resetAllErrors(w)

##     # normFactors (such as mu_Top, mu_WZ, etc) need to have their errors set
##     # to a small number for the before the fit plots
##     normList = configMgr.normList
##     for norm in normList:
##         if norm in fc.measurements[0].paramSettingDict.keys():
##             if fc.measurements[0].paramSettingDict[norm][0]:
##                 continue
##         normfac = w.var(norm)
##         if normfac:
##             normfac.setError(0.001)
##             print "Uncertainty on parameter: ", norm, " set to 0.001"

    # set the flag for plotting ratio or pull distribution under the plot
    # plotRatio = False means that a pull distribution will be drawn
    plotRatio = True

    # get a list of all floating parameters for all regions
    simPdf = w.pdf("simPdf")
    mc = Util.GetModelConfig(w)
    obsSet = mc.GetObservables()
    floatPars = Util.getFloatParList(simPdf, obsSet)

    # create an RooExpandedFitResult encompassing all the
    # regions/parameters & save it to workspace
    expResultBefore = RooExpandedFitResult(floatPars)
    Util.ImportInWorkspace(w, expResultBefore,
                            "RooExpandedFitResult_beforeFit")

##     # plot before fit
##     if drawBeforeAfterFit:
##         Util.PlotPdfWithComponents(w, fc.name, plotChannels, "beforeFit",
##                                    expResultBefore, toyMC, plotRatio)

    # fit of all regions
    result = Util.FitPdf(w, fitChannels, lumiConst, toyMC)

    # create an RooExpandedFitResult encompassing all the regions/parameters
    # with the result & save it to workspace
    expResultAfter = RooExpandedFitResult(result, floatPars)
    Util.ImportInWorkspace(w, expResultAfter, "RooExpandedFitResult_afterFit")

    # plot after fit
    if drawBeforeAfterFit:
        Util.PlotPdfWithComponents(w, fc.name, plotChannels, "afterFit",
                                   expResultAfter, toyMC, plotRatio)
        #plot each component of each region separately with propagated
        #error after fit  (interesting for debugging)
        #Util.PlotSeparateComponents(fc.name, plotChannels,
        #                             "afterFit", result,toyMC)

        # plot correlation matrix for result
        Util.PlotCorrelationMatrix(result)
        # plot likelihood
        #    plotPLL = False
        #         Util.PlotNLL(w, expResultAfter, plotPLL, "", toyMC)

    if toyMC:
        Util.WriteWorkspace(w, fc.wsFileName, toyMC.GetName())
    else:
        Util.WriteWorkspace(w, fc.wsFileName)

    try:
        if not result == None:
            result.Print()
            return result
    except:
        pass
    return



if __name__ == "__main__":
    from configManager import configMgr
    from prepareHistos import TreePrepare, HistoPrepare
    log = Logger("HistFitter")

    configMgr.readFromTree = False
    configMgr.executeHistFactory = False
    runInterpreter = False
    runFit = False
    printLimits = False
    doHypoTests = False
    doUL = True           # default is exclusion. goes toegether with doHypoTests
    drawBeforeAfterFit              = False
    drawCorrelationMatrix         = False
    drawSeparateComponents = False
    drawLogLikelihood               = False
    pickedSRs = []
    runToys = False

    FitType = enum('FitType','Discovery , Exclusion , Background')
    myFitType=FitType.Background
    doValidation = False
    
    print "\n * * * Welcome to HistFitter * * *\n"

    import os, sys
    import getopt
    def usage():
        print "HistFitter.py [-L loglevel] [-i] [-t] [-w] [-x] [-f] [-l] [-p] [-d] [-n nTOYs] [-s seed] [-r SRs] [-g gridPoint] [-b bkgParName,value] [--draw plotOpts] <configuration_file>\n"
        print "(all OFF by default. Turn steps ON with options)"
        print "-L   set log level (VERBOSE, DEBUG, INFO, WARNING, ERROR, FATAL, ALWAYS; default INFO)"
        print "-t   re-create histograms from TTrees (default: %s)" % (configMgr.readFromTree)
        print "-w   re-create workspace from histograms (default: %s)" % (configMgr.executeHistFactory)
        print "-x   use XML and hist2workspace, instead of HistFactory python methods, to generate workspaces (default: %s)" % (configMgr.writeXML)
        print "-f   fit the workspace (default: %s)" % (configMgr.executeHistFactory)
        print "-n   <nTOYs> sets number of TOYs (<=0 means to use real data, default: %i)" % configMgr.nTOYs
        print "-s   <number> set the random seed for toy generation (default is CPU clock: %i)" % configMgr.toySeed
        print "-a   use Asimov dataset for fitting and plotting (default: %i)" % configMgr.useAsimovSet
        print "-i   stays in interactive session after executing the script (default %s)" % runInterpreter
        print "-l   make limit plot of workspace (default %s)" % printLimits
        print "-p   run (exclusion) hypothesis test on workspace (default %s)" % doHypoTests
        print "--pz run the discovery hypothesis test (default %s)" % (not doUL)
        print "-g   <grid points to be processed> - give as comma separated list"
        print "-r   signal region to be processed - give as comma separated list (default = all)"
        print "-d   Draw before/after fit plots of all channels (default: %s)" % drawBeforeAfterFit,  "  additional arguments 'allPlots' or comma separated 'beforeAfter, corrMatrix, sepComponents, likelihood'"
        print "-b   when doing hypotest, correct bkg-level to: bkg strength parameter, bkg value"
        print "-0   removes empty bins when drawing the data histograms with (complimentary to -d)"
        print "--ty run toys (default with mu)."
        print "--draw with arguments 'allPlots' or comma separated 'beforeAfter, corrMatrix, sepComponents, likelihood'"

        print "\nAlso see the README file.\n"
        print "Command examples:"
        print "HistFitter.py -i python/MySusyFitterConfig.py           #only runs initialization in interactive mode (try e.g.: configMgr.<tab>)"
        print "HistFitter.py -t -w -f python/MySusyFitterConfig.py     #runs all steps (TTree->Histos->Workspace->Fit) in batch mode"
        print "HistFitter.py -f -i python/MySusyFitterConfig.py        #only fit and plot, using existing workspace, in interactive session"
        print "HistFitter.py -s 666 -f python/MySusyFitterConfig.py    #fit a TOY dataset (from seed=666) and prints RooFitResult"
        print "\nNote: examples of input TTrees can be found in /afs/cern.ch/atlas/groups/susy/1lepton/samples/"
        sys.exit(0)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "xd0twfinals:r:b:g:L:p:",["bkgfit","exclfit","discfit","vr","pz","ty","draw="])
        configFile = str(args[0])
    except:
        usage()

    
    for opt,arg in opts:
        #print opt,arg
        if opt == '--bkgfit':
            myFitType=FitType.Background
        elif opt == '--exclfit':
            myFitType=FitType.Exclusion
        elif opt == '--discfit':
            myFitType=FitType.Discovery
        elif opt == '--vr':
            doValidation=True
        elif opt == '-t':
            configMgr.readFromTree=True
        elif opt == '-w':
            configMgr.executeHistFactory = True
        elif opt == '-x':
            configMgr.writeXML = True
        elif opt == '-f':
            runFit = True
        elif opt == '-n':
            configMgr.nTOYs = int(arg)
        elif opt == '-i':
            runInterpreter = True
        elif opt == '-L':
            #2nd argument forces the log level to be locked for python scripts
            if len(arg) == 1: #assume this is an integer log level
                log.setLevel(int(arg),True)
            else:
                log.setLevel(arg,True) #can take both strings and ints, does its own checking 
        elif opt == '-l':
            printLimits = True
        elif opt == '-p':
            doHypoTests = True
        elif opt == '--pz':
            doHypoTests = True
            doUL = False
        elif opt == '-d':
            drawBeforeAfterFit = True
        elif opt == '--draw':
            drawArgs = arg.split(',')
            #print "drawArgs(",drawArgs, ")  length = ", len(drawArgs)
            if len(drawArgs) == 1 and drawArgs[0] == "allPlots":
                drawBeforeAfterFit = True
                drawCorrelationMatrix         = True
                drawSeparateComponents = True
                drawLogLikelihood               = True
            elif len(drawArgs)>0:
                for drawArg in drawArgs:
                    if drawArg == "beforeAfter":
                        drawBeforeAfterFit = True
                    elif drawArg == "corrMatrix":
                        drawCorrelationMatrix         = True
                    elif drawArg == "sepComponents":
                        drawSeparateComponents = True
                    elif drawArg == "likelihood":
                        drawLogLikelihood               = True
                    else:
                        log.fatal("Wrong draw argument: %s\n  Possible draw arguments are 'allPlots' or comma separated 'beforeAfter, corrMatrix, sepComponents, likelihood'" % drawArg)
        elif opt == '-0':
            configMgr.removeEmptyBins = True
        elif opt == '-s':
            configMgr.toySeedSet = True
            configMgr.toySeed = int(arg)
        elif opt == '-a':
            configMgr.useAsimovSet = True
        elif opt == '-g':
            sigSamples = arg.split(',')
        elif opt == '-r':
            pickedSRs = arg.split(',')
        elif opt == '--ty':
            runToys = True
        elif opt == '-b':
            bkgArgs = arg.split(',')
            if len(bkgArgs) == 2:
                configMgr.SetBkgParName(bkgArgs[0])
                configMgr.SetBkgCorrVal(float(bkgArgs[1]))
                configMgr.SetBkgChlName("")
            elif len(bkgArgs) >= 3 and len(bkgArgs) % 3 == 0:
                for iChan in xrange(len(bkgArgs) / 3):
                    iCx = iChan * 3
                    configMgr.AddBkgChlName(bkgArgs[iCx])
                    configMgr.AddBkgParName(bkgArgs[iCx+1])
                    configMgr.AddBkgCorrVal(float(bkgArgs[iCx+2]))
                    continue
        pass
    gROOT.SetBatch(not runInterpreter)

    #mandatory user-defined configuration
    execfile(configFile)

    #standard execution from now on.
    configMgr.initialize()

    # initialize: set the toy seed
    RooRandom.randomGenerator().SetSeed(configMgr.toySeed)

    #runs Trees->histos and/or histos->workspace according to specifications
    if configMgr.readFromTree or configMgr.executeHistFactory:
        configMgr.executeAll()

    if runFit:
        if len(configMgr.fitConfigs) > 0:
      #      r = GenerateFitAndPlot(configMgr.fitConfigs[0], drawBeforeAfterFit)
            #r=GenerateFitAndPlot(configMgr.fitConfigs[1],drawBeforeAfterFit)
            #r=GenerateFitAndPlot(configMgr.fitConfigs[2],drawBeforeAfterFit)
            #for idx in range(len(configMgr.fitConfigs)):
            #    r=GenerateFitAndPlot(configMgr.fitConfigs[idx],drawBeforeAfterFit)
            r = GenerateFitAndPlotCPP(configMgr.fitConfigs[0], drawBeforeAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood)
            pass
        #configMgr.cppMgr.fitAll()
        log.info("\nr0=GenerateFitAndPlot(configMgr.fitConfigs[0],False)")
        log.info("r1=GenerateFitAndPlot(configMgr.fitConfigs[1],False)")
        log.info("r2=GenerateFitAndPlot(configMgr.fitConfigs[2],False)")
        log.info(" OR \n GenerateFitAndPlotCPP(configMgr.fitConfigs[0], drawBeforeAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood)")
        log.info("    where drawBeforeAfterFit, drawCorrelationMatrix, drawSeparateComponents, drawLogLikelihood are booleans")

        pass

    if printLimits:
        for fc in configMgr.fitConfigs:
            if len(fc.validationChannels) > 0:
                raise(Exception, "Validation regions should be turned off for setting an upper limit!")
            pass
        configMgr.cppMgr.doUpperLimitAll()
        pass

    if doHypoTests:
        for fc in configMgr.fitConfigs:
            if len(fc.validationChannels) > 0:
                raise(Exception,"Validation regions should be turned off for doing hypothesis test!")
            pass
        configMgr.cppMgr.doHypoTestAll('results/',doUL)
        pass

    if runToys and configMgr.nTOYs > 0 and doHypoTests == False and printLimits == False and runFit == False:
        configMgr.cppMgr.runToysAll()
        pass

    if runInterpreter:
        from code import InteractiveConsole
        from ROOT import Util
        cons = InteractiveConsole(locals())
        cons.interact("Continuing interactive session... press Ctrl+d to exit")
        pass

    log.info("Leaving HistFitter... Bye!")
