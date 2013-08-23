import os
import os.path
import ConfigParser


class Config(object):

    def __init__(self, config_path=""):
        self.cp = ConfigParser.ConfigParser()
        self.section_default = 'docfu'
        self.config_path = config_path

    def read(self):
        self.cp.read(self.config_path)

    def __getattr__(self, name, section=''):
        if section:
            return self.cp.get(section, name)
        return self.cp.get(self.section_default, name)
