import re
import ROOT
import collections

#Tuple containing (value, error) with named fields
ValueErrorTuple = collections.namedtuple('ValueErrorTuple', ['value', 'error'])

#SIP method separates 2e2mu and 2mu2e channels
#The 2e2mu channel of FiducialXS is known as 2e2mu-2mu2e
def convertFiducialXSChannelToSipChannel(channelFiducialXS):
    if channelFiducialXS == '2e2mu':
        return '2e2mu-2mu2e'
    else:
        return channelFiducialXS

#Holds Z+jets configuration read from file, for a given year
class ZjetsData:
    def __init__(self, year, pathPrefix=""):
        self.year = year
        with open(pathPrefix + "ZX_estimation/" + year + "/ZX_SIP_method_results.txt") as f:
            self.txt_file_content = f.read()
    
    def getValue(self, key):
        regex = r"^" + key + r" = ([0-9\.]+)$" #Match begining of line then key then " = " then a number then end of line
        match = re.search(regex, self.txt_file_content, re.MULTILINE)
        return float(match.group(1)) # return the parenthesis match which should be the float value we want
    
    """Returns tuple (value, error) for Z+X estimation for given SIP method channel. 2e2mu and 2mu2e are speparate channels"""
    def getNormCorrected(self, channel):
        return ValueErrorTuple(self.getValue("NormCorrected_" + channel), self.getValue("NormCorrectedError_" + channel))
    
    """Return relative error on tight inclusive ratio, for nuisance of ratio correlated across channels"""
    def getRatioTightInclusiveRelativeError(self):
        return self.getValue("RatioTightInclusive_relativeError")
    
    """Get location parameter of Landau for Z+X shape. Retrun tuple (value, error)"""
    def getShapeLocationParameter(self, channel):
        return ValueErrorTuple(self.getValue("Shape_locationParameter_" + channel), self.getValue("Shape_locationParameterError_" + channel))
    
    def getShapeWidthParameter(self, channel):
        return ValueErrorTuple(self.getValue("Shape_widthParameter_" + channel), self.getValue("Shape_widthParameterError_" + channel))


#Holds RooFit objects used for Z+jets shape and normalization
class ZjetsRoofitObjects:
    
    """ data is Zjets_data object, m4l_mass is a RooRealVar 
    mergedChannelName is either 2X2e or 2X2mu, used for naming the shape parameters
    shapeChannel is the individual channel name (2e2mu and 2mu2e are different) used to extract the shape
    """
    def __init__(self, data, m4l_mass, mergedChannelName, shapeChannel): 
        self.landauLocationParamName = "bkg_zjets_" + mergedChannelName + "_" + data.year + "_landau_locationParam"
        self.landauShapeParamName = "bkg_zjets_" + mergedChannelName + "_" + data.year + "_landau_scaleParam"
        #bkg_zjets_norm is not used anymore
        #self.zjets_norm = ROOT.RooRealVar("bkg_zjets_norm", "Normalization of Z+jets background", data.getValue("Norm"))
        #zjets_norm.setError(getFloatValueFromFileText(file_data, "NormError"))

        self.landauLocation = ROOT.RooRealVar(self.landauLocationParamName, "Z+jets Landau location parameter", data.getShapeLocationParameter(shapeChannel).value)
        #landauLocation.setError( data.getShapeLocationParameter(shapeChannel)[1])

        self.landauScale = ROOT.RooRealVar(self.landauShapeParamName, "Z+jets Landau scale parameter", data.getShapeWidthParameter(shapeChannel).value)
        #landauScale.setError(data.getShapeWidthParameter(shapeChannel)[1])

        self.zjets_pdf = ROOT.RooLandau("bkg_zjets", "Landau for Z+jets bkg, "+mergedChannelName, m4l_mass, self.landauLocation, self.landauScale)

#List of all Z+X nuisance names for given years
def getAllZXNormNuisances(years):
    return []
    # nuisances_names = ['CMS_zz4l_Zjets_ratio_systematic']
    # for year in years:
    #     for mergedChannel in ['2X2e', '2X2mu']:
    #         nuisances_names.append('CMS_zz4l_Zjets_' + year + '_' + mergedChannel)
    # return nuisances_names 

class ZjetsDatacardHelper:
    #xsecChannel is the channel used for fiducial cross-section, ie 2e2mu is merged
    def __init__(self, year, xsecChannel, zjetsData):
        self.year = year
        self.channel = xsecChannel
        self.pathPrefix = ''
        self.zjetsData = zjetsData
    
    #Return the list of processes 
    def getListOfProcessNames(self):
        #2e2mu is merged from 2e2mu(SIP method) and 2mu2e(SIP method) therefore two processes : bkg_zjets_2X2mu AND bkg_zjets_2X2e
        #return ['bkg_zjets_2X2e', 'bkg_zjets_2X2mu']
        return ['bkg_zjets']
    
    #Number of background process bin for the channel
    def getNumberOfProcesses(self):
        return len(self.getListOfProcessNames())

    def getRates(self):
        return['1'] #Completely float Z+X
        # if (self.channel == '4mu' or self.channel == '4e'):
        #     if (self.channel == '4mu'):
        #         #       2X2e   2X2mu
        #         return ['0', str(self.zjetsData.getNormCorrected(self.channel).value)]
        #     else:
        #         #                           2X2e                           2X2mu
        #         return [str(self.zjetsData.getNormCorrected(self.channel).value), '0']
        # elif (self.channel == '2e2mu'):
        #     #2e2mu is merged from 2e2mu(SIP method) and 2mu2e(SIP method) therefore two processes : bkg_zjets_2X2mu AND bkg_zjets_2X2e
        #     #order matters :                            2X2e                                            2X2mu                   
        #     return [str(self.zjetsData.getNormCorrected('2mu2e').value), str(self.zjetsData.getNormCorrected('2e2mu').value)]
    
    #Get the relative uncertainty for ratio systematic
    def getRatioSystematicRelativeUncertainty(self):
        return self.zjetsData.getRatioTightInclusiveRelativeError()
    
    #return the value to put for the nuisance for the datacard as a string ('-' if no impact)
    def getNuisanceValues(self, mergedChannel):
        singleSIPChannel = self.channel
        if (mergedChannel == '2X2e'):
            if (self.channel == '4mu'):
                return '-'
            elif (self.channel == '2e2mu'):
                singleSIPChannel = '2mu2e'
            #4e : no change needed
        elif (mergedChannel == '2X2mu'):
            if (self.channel == '4e'):
                return '-'
            #2e2mu or 4mu : no change needed
        else:
            assert False

        (norm_value, norm_error) = self.zjetsData.getNormCorrected(singleSIPChannel)
        #norm_error is the statistical error on Loose+ID+ISO ratio

        return str(1 +  norm_error/norm_value)
                


