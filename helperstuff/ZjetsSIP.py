import re
import ROOT



def getPathToZjetsInput(year, channel, pathPrefix=""):
    return pathPrefix + "zjets_wp/" + year + "/bkg_zjets_" + channel + ".txt"

def getZjets_txt(year, channel, pathPrefix=""):
    with open(getPathToZjetsInput(year, channel, pathPrefix)) as f:
        return f.read()

#Holds Z+jets configuration read from file, for a given year and channel
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
    landauLocationParamName = "bkg_zjets_landau_locationParam"
    landauShapeParamName = "bkg_zjets_landau_scaleParam"
    def __init__(self, data, m4l_mass): #data is Zjets_data object, m4l_mass is a RooRealVar 
        self.zjets_norm = ROOT.RooRealVar("bkg_zjets_norm", "Normalization of Z+jets background", data.getValue("Norm"))
        #zjets_norm.setError(getFloatValueFromFileText(file_data, "NormError"))

        self.landauLocation = ROOT.RooRealVar(self.landauLocationParamName, "Z+jets Landau location parameter", data.getValue("locationParameter"))
        #landauLocation.setError(getFloatValueFromFileText(file_data, "locationParameterError"))

        self.landauScale = ROOT.RooRealVar(self.landauShapeParamName, "Z+jets Landau scale parameter", data.getValue("scaleParameter"))
        #landauScale.setError(getFloatValueFromFileText(file_data, "scaleParameterError"))

        self.zjets_pdf = ROOT.RooLandau("bkg_zjets", "Landau for Z+jets bkg", m4l_mass, self.landauLocation, self.landauScale)

def getAllZXShapeNuisances(years):
    nuisances_names = []
    for year in years:
        for channel in ['4e', '4mu', '2e2mu']:
            nuisances_names.append('bkg_zjets_' + channel + '_landau_locationParam_' + year)
    return nuisances_names