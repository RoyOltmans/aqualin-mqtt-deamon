#-------------------------------------------------------------------------------
# Name:        main_Utils
# Purpose:     Class functions libary
#
# Author:      roy.oltmans
#
# Created:     23-10-2014
# Copyright:   (c) roy.oltmans 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, ConfigParser

class tools(object):
    #Fetch Configuration
    def fetchConfig(self):
        Config = ConfigParser.ConfigParser()
        ConfigFilePath = os.path.dirname(os.path.abspath(__file__)).replace(' ','\ ') + "/config.ini"
        Config.read(ConfigFilePath)
        return Config