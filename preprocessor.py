# coding=utf-8
import xml.etree.ElementTree as ET


class PreProcessor(object):

    def __init__(self):
        self.tex_constructors = ['set', 'list', 'vector']

    def process(self, mathml_string_data):
        assert mathml_string_data.startswith('<')
        mathml_string_data = self.__identify_constructors(mathml_string_data)
        mathml_string_data = self.__identify_applies(mathml_string_data)
        root = ET.fromstring(mathml_string_data)
        result = []
        for elem in root.iter():
            if elem.tag == 'math':
                pass
            elif elem.tag == 'ci':
                if 'type' in elem.keys():
                    if elem.attrib['type'] == 'function':
                        result.append(elem.attrib['type'])
                result.append(elem.text.upper() if len(elem.text) <= 2 else elem.text)
            elif elem.tag == 'cn':
                result.append(elem.text.upper())
            elif elem.tag == 'end':
                result.append('end-apply')
            elif elem.tag == 'end_constructor':
                result.append('end-constructor')
            else:
                result.append(elem.tag)
        return result

    @staticmethod
    def __identify_applies(mathml_string):
        return mathml_string.replace('</apply>', '<end></end></apply>')

    def __identify_constructors(self, mathml_string):
        result = mathml_string
        identified_constructor = filter(lambda x: x in mathml_string, self.tex_constructors)
        for constructor in identified_constructor:
            open_constructor_tag = '<' + constructor + '>'
            close_constructor_tag = '</' + constructor + '>'
            result = result.replace(open_constructor_tag, '<apply>' + open_constructor_tag).\
                replace(close_constructor_tag, close_constructor_tag + '</apply>')
        result = result.replace(u'ℤ', 'integers')
        if '&' in mathml_string:
            result = result.replace('&', '').replace(';', '')
        return result