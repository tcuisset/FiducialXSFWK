import re
### ------- lxplus -------
# path = {
# 'eos_path_sig': '/eos/user/a/atarabin/MC_samples/',
# 'eos_path': '/eos/user/a/atarabin/',
# 'eos_path_FR': '/eos/cms/store/group/phys_higgs/cmshzz4l/cjlst/RunIILegacy/200205_CutBased/'
#
# }


### ------- polui UL -------
## To get ReReco path, remove MC_samples_UL
path = {
'eos_path_sig': '/grid_mnt/data__data.polcms/cms/tarabini/HZZ4l/MC_samples_UL/',  ## If you set to ReReco, change from %i_MELA to MC_samples/%i_MELA
'eos_path': '/grid_mnt/data__data.polcms/cms/tarabini/HZZ4l/',
'eos_path_FR': '/grid_mnt/data__data.polcms/cms/tarabini/HZZ4l/', ## In RunTemplated if you set to  ReReco change name from FakeRates_SS_%i.root to newData_FakeRates_SS_%i.root
}

def getFloatValueFromFileText(file_text, key):
    regex = r"^" + key + r" = ([0-9\.]+)$"
    #print file_text
    #print regex
    match = re.search(regex, file_text, re.MULTILINE)
    return float(match.group(1)) # return the parenthesis match which should be the float value we want

def getPathToZjetsInput(year, channel, pathPrefix=""):
    return pathPrefix + "zjets_wp/" + year + "/bkg_zjets_" + channel + ".txt"

def getZjets_txt(year, channel, pathPrefix=""):
    with open(getPathToZjetsInput(year, channel, pathPrefix)) as f:
        return f.read()