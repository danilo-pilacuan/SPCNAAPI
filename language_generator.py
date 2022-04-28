from configobj import ConfigObj
from os import path
import re


class LanguageGenerator(object):

    k_constants = 'constantes'
    k_operators = 'operadores'

    def generate_sub_language(self, stack, logging=False):
        """
        Given a stack, it will return the natural language representation of it.
        Description:
            while apply is present in stack, it means that there is still some math expression to translate.
            So it gets the operator that we need to translate (with self.get_operator) and then it
            replaces the atomic translation in the stack
            They repeat the same process until there is no apply in stack, so we consider this fact as we end and in the
            first position of the stack we have the final transcription.
        :param stack: stack obtained of preProcessor
        :param logging:
        :return:
        """
        self.replace_constants(stack)
        self.reorganize(stack)
        while 'apply' in stack:
            i, j, temp_stack, operator, arity, key_op = self.get_operator(stack)
            stack = stack[:i] + [self.replace_values(key_op, operator, arity, temp_stack[2:])] + stack[j+1:]
            if logging:
                print stack
        assert len(stack) == 1
        return stack[0]

    @staticmethod
    def reorganize(stack):
        if 'inverse' in stack:
            i = stack.index('inverse')
            stack[i-1], stack[i] = stack[i], stack[i-1]
            j = stack.index('function')
            i = stack.index('end-apply', j)
            stack[i + 1], stack[i] = stack[i], stack[i + 1]

    def get_operator(self, stack):
        """
        It returns six elements, given a stack this will return the position where the apply starts
        and the position where the apply ends. (i and j)
        the temporary stack, containing the part of the stack from i to j
        the operator is the transcription for key_op
        arity is the arity of the operator that we are looking for
        key_op is the key or tag of cmathml representation of math operator, we need to look up
         in the language.template for the transcription
        :param stack:
        :return:
        """
        i = self.__rindex(stack, 'apply')
        j = stack.index('end-apply', i)
        temp_stack = stack[i:j]
        key_op = temp_stack[1]
        if key_op not in self.get_valids_operators_from_template():
            raise NotImplementedError('%s is not implemented' % key_op)
        config = self.get_language_template()
        operator = config[self.k_operators][key_op]
        arity = len(temp_stack) - 2
        if isinstance(operator, list):
            for op in operator:
                if op.count('$')/2 == arity:
                    operator = op
                    break
        return i, j, temp_stack, operator, arity, key_op

    @staticmethod
    def __rindex(list_o, elem):
        return len(list_o) - list(reversed(list_o)).index(elem) - 1

    @staticmethod
    def prepare_operator(key_op, operator, values):
        """
        Helper that we need to replace the transcription, it is needed to fill when the replacing is not so direct
        """
        arity = len(values)
        if key_op in ['sum', 'product']:
            i = values.index('bvar')
            operator = operator.replace('$bvar$', values[i+1])
            values.remove(values[i+1])
            values.remove('bvar')
            if 'lowlimit' in values:
                i = values.index('lowlimit')
                operator = operator.replace('$lowlimit$', values[i+1])
                values.remove(values[i+1])
                values.remove('lowlimit')
                i = values.index('uplimit')
                operator = operator.replace('$uplimit$', values[i+1])
                values.remove(values[i+1])
                values.remove('uplimit')
                arity -= 6
            elif 'condition' in values:
                i = values.index('condition')
                operator = operator.replace('')
                # TODO Fix here
        elif key_op in ['max', 'min', 'list', 'vector']:
            values = [' '.join(values)]
            arity = 1
        elif key_op == 'limit':
            i = values.index('bvar')
            operator = operator.replace('$bvar$', values[i+1])
            values.remove(values[i+1])
            values.remove('bvar')
            i = values.index('lowlimit')
            operator = operator.replace('$lowlimit$', values[i+1])
            values.remove(values[i+1])
            values.remove('lowlimit')
            arity -= 4
        elif key_op == 'log':
            if 'logbase' in values:
                i = values.index('logbase')
                operator = operator.replace('$base$', 'base ' + values[i+1])
                values.remove(values[i+1])
                values.remove('logbase')
                arity -= 2
            else:
                operator = operator.replace('$base$ ', '')
        elif key_op == 'set':
            if 'bvar' in values:
                operator = operator[0]
                i = values.index('bvar')
                operator = operator.replace('$bvar$', values[i+1])
                values.remove(values[i+1])
                values.remove('bvar')
                i = values.index('condition')
                operator = operator.replace('$condition$', values[i+1])
                values.remove(values[i+1])
                values.remove('condition')
                arity -= 4
            else:
                operator = operator[1]
                values = [', '.join(values)]
                arity = 1
        elif key_op == 'root':
            if 'degree' in values:
                i = values.index('degree')
                operator = operator.replace('$degree$', values[i+1])
                values.remove(values[i+1])
                values.remove('degree')
                arity -= 2
            else:
                operator = operator.replace('$degree$', 'cuadrada')
        return operator, values, arity

    def replace_values(self, key_op, operator, arity, values):
        """
        Until Arity is 1, it will be replacing the values of the tanscription with the values of the stack
        :param key_op: key_op to obtain transcription
        :param operator: transcription from template
        :param arity: arity
        :param values: Values of the stack
        :return:
        """
        assert arity == len(values), "There is more values to unpack"
        result, values, arity = self.prepare_operator(key_op, operator, values)
        if arity == 1:
            return '(' + result.replace("$VAR$", values[0]) + ')'
        elif arity == 2:
            result = re.sub(r'(\$VAR\$)', values[0], result, count=1)
            result = re.sub(r'(\$VAR\$)', values[1], result, count=1)
            return '(' + result + ')'
        elif arity >= 3:
            result = re.sub(r'(\$VAR\$)', values[0], result, count=1)
            new_operator = re.sub(r'(\$VAR\$)', operator, result, count=1)
            return self.replace_values(key_op, new_operator, arity - 1, values[1:])

    def replace_constants(self, stack):
        config = self.get_language_template()
        constants = self.get_valid_constants_from_template()
        for constant in constants:
            if constant in stack:
                c_tr = config[self.k_constants][constant.lower()]
                i = stack.index(constant)
                stack.insert(i, c_tr)
                stack.remove(constant)

    @staticmethod
    def get_language_template():
        location_file = path.join(path.dirname(__file__), 'language.template')
        return ConfigObj(location_file)

    def get_valids_operators_from_template(self):
        config = self.get_language_template()
        return config[self.k_operators].keys()

    def get_valid_constants_from_template(self):
        config = self.get_language_template()
        return config[self.k_constants].keys()
