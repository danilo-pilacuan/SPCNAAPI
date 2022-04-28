import requests
from xml.sax.saxutils import unescape
import re


class SnuggleTexClient(object):

    def __init__(self):
        """
        Initialize all the needed to communicate with SnuggleTex
        """
        self.url = 'http://192.168.0.100:8080/snuggletex-webapp-1.2.2'
        self.uris = {
            'mathml_input': '/ASCIIMathMLUpConversionDemo',
            'latex_input': '/UpConversionDemo'
        }
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.13) Gecko/20080311 Firefox/2.0.0.13"
        }
        requests.packages.urllib3.disable_warnings()

    def latex_to_mathml(self, latex):
        """
        Handle requests to snuggletex API to convert the LaTeX to MathML
        """
        url = self.url + self.uris['latex_input']
        payload = {
            'input': latex,
        }
        request = requests.post(url, data=payload, headers=self.headers, verify=False)
        request.encoding = 'utf-8'
        cmathml = self.__parse_cmathml(request.text)
        if not cmathml:
            cmathml = self.__manage_unhandled_input(latex)
        return cmathml

    def pmathml_to_cmathml(self, pmathml):
        """
        Handle requests to snuggletex API to convert the Ascii math to MathML
        """
        url = self.url + self.uris['mathml_input']
        payload = {
            'asciiMathML': pmathml,
        }
        request = requests.post(url, data=payload, headers=self.headers, verify=False)
        request.encoding = 'utf-8'
        cmathml = self.__parse_cmathml_content(request.text)
        return cmathml

    @staticmethod
    def __parse_cmathml(webpage_text):
        cmathml_box = re.search('<h3>Content MathML</h3>(.|\n)*?<h3>Maxima Input Syntax</h3>', webpage_text).group()
        try:
            cmathml_string = re.search('&lt;math(.|\n)*?/math&gt;', cmathml_box).group()
            cmathml_string = '\n'.join(cmathml_string.split('\n')[1:-1])
            return unescape(cmathml_string.strip())
        except AttributeError:
            return None

    @staticmethod
    def __parse_cmathml_content(webpage_text):
        mode = 0
        cmathml = []
        for k in webpage_text.split('\n'):
            if 'conversion to Content MathML' in k:
                mode = 1
                continue
            if mode == 1:
                if '<h3>Maxima Input Form</h3>' in k:
                    mode = 0
                    continue
                cmathml.append(k)
        cmathml = '\n'.join(cmathml[2:])
        return '<math>\n' + unescape(cmathml) + '\n</math>'

    def __manage_unhandled_input(self, tex_string):
        mathml_string = None
        if tex_string.startswith('\sum_'):
            vbar, lowlimit, uplimit, body = re.search(r'\\sum_{(.)=(.*)}\^(\S*) (\S*)', tex_string).groups()
            snuggletex = SnuggleTexClient()
            bodymathml = self.latex_to_mathml(body)
            mathml_string = """<apply><sum/><bvar><ci>%s</ci></bvar><lowlimit><ci>%s</ci></lowlimit><uplimit><ci>%s</ci></uplimit>%s</apply>""" % (vbar, lowlimit, uplimit, bodymathml)
        return mathml_string