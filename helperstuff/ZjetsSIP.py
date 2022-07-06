import re
import ROOT



def getPathToZjetsInput(year, channel, pathPrefix=""):
    return pathPrefix + "zjets_wp/" + year + "/bkg_zjets_" + channel + ".txt"

def getZjets_txt(year, channel, pathPrefix=""):
    with open(getPathToZjetsInput(year, channel, pathPrefix)) as f:
        return f.read()

#SIP method separates 2e2mu and 2mu2e channels
#The 2e2mu channel of FiducialXS is known as 2e2mu-2mu2e
def convertFiducialXSChannelToSipChannel(channelFiducialXS):
    if channelFiducialXS == '2e2mu':
        return '2e2mu-2mu2e'
    else:
        return channelFiducialXS

#Holds Z+jets configuration read from file, for a given year and SIP method channel
class ZjetsData:
    def __init__(self, year, channel, pathPrefix=""):
        self.year = year
        self.channel = channel
        self.txt_file_content = getZjets_txt(year, channel, pathPrefix)
    
    def getValue(self, key):
        regex = r"^" + key + r" = ([0-9\.]+)$"
        match = re.search(regex, self.txt_file_content, re.MULTILINE)
        return float(match.group(1)) # return the parenthesis match which should be the float value we want
    


#Holds RooFit objects used for Z+jets shape and normalization
class ZjetsRoofitObjects:
    
    """ data is Zjets_data object, m4l_mass is a RooRealVar 
    """
    def __init__(self, data, m4l_mass, mergedChannelName): 
        self.landauLocationParamName = "bkg_zjets_" + mergedChannelName + "_" + data.year + "_landau_locationParam"
        self.landauShapeParamName = "bkg_zjets_" + mergedChannelName + "_" + data.year + "_landau_scaleParam"
        #bkg_zjets_norm is not used anymore
        #self.zjets_norm = ROOT.RooRealVar("bkg_zjets_norm", "Normalization of Z+jets background", data.getValue("Norm"))
        #zjets_norm.setError(getFloatValueFromFileText(file_data, "NormError"))

        self.landauLocation = ROOT.RooRealVar(self.landauLocationParamName, "Z+jets Landau location parameter", data.getValue("locationParameter"))
        #landauLocation.setError(getFloatValueFromFileText(file_data, "locationParameterError"))

        self.landauScale = ROOT.RooRealVar(self.landauShapeParamName, "Z+jets Landau scale parameter", data.getValue("scaleParameter"))
        #landauScale.setError(getFloatValueFromFileText(file_data, "scaleParameterError"))

        self.zjets_pdf = ROOT.RooLandau("bkg_zjets_"+mergedChannelName, "Landau for Z+jets bkg, "+mergedChannelName, m4l_mass, self.landauLocation, self.landauScale)


def getAllZXNormNuisances(years):
    nuisances_names = ['CMS_zz4l_Zjets_ratio_systematic']
    for year in years:
        for mergedChannel in ['2X2e', '2X2mu']:
            nuisances_names.append('CMS_zz4l_Zjets_' + year + '_' + mergedChannel)
    return nuisances_names 

class ZjetsDatacardHelper:
    #xsecChannel is the channel used for fiducial cross-section, ie 2e2mu is merged
    def __init__(self, year, xsecChannel):
        self.year = year
        self.channel = xsecChannel
        self.pathPrefix = ''

   
    
    #Return the list of processes 
    def getListOfProcessNames(self):
        #2e2mu is merged from 2e2mu(SIP method) and 2mu2e(SIP method) therefore two processes : bkg_zjets_2X2mu AND bkg_zjets_2X2e
        return ['bkg_zjets_2X2e', 'bkg_zjets_2X2mu']
    
    #Number of background process bin for the channel
    def getNumberOfProcesses(self):
        return len(self.getListOfProcessNames())

    def getRates(self):
        if (self.channel == '4mu' or self.channel == '4e'):
            data = ZjetsData(self.year, self.channel, self.pathPrefix)
            if (self.channel == '4mu'):
                #       2X2e   2X2mu
                return ['0', str(data.getValue('Norm'))]
            else:
                #       2X2e                        2X2mu
                return [str(data.getValue('Norm')), '0']
        elif (self.channel == '2e2mu'):
            #2e2mu is merged from 2e2mu(SIP method) and 2mu2e(SIP method) therefore two processes : bkg_zjets_2X2mu AND bkg_zjets_2X2e
           data_2e2mu = ZjetsData(self.year, '2e2mu', self.pathPrefix)
           data_2mu2e = ZjetsData(self.year, '2mu2e', self.pathPrefix)
           #order matters
           return [str(data_2mu2e.getValue('Norm')), str(data_2e2mu.getValue('Norm'))]
    
    #Get the relative uncertainty for ratio systematic
    def getRatioSystematicRelativeUncertainty(self):
        #TODO
        return 0.4
    
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
        
        data = ZjetsData(self.year, singleSIPChannel, self.pathPrefix)

        result = 1 + data.getValue('NormErrorRatioStatOnly')/data.getValue('Norm')

        return str(result)
                


