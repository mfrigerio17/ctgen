import sympy, enum, re, copy, numbers
from collections import OrderedDict

import kgprim.values as numeric_argument
import kgprim.ct.models
import kgprim.ct.metadata


digit_matcher = re.compile("^[0-9]")
def symbolicExpressionToIdentifier(symb_expr):
    '''
    Turn a symbolic math expression into a string suitable as an identifier to
    be used in code
    '''
    s = str(symb_expr)
    s = s.replace(" ", "").replace(".","").replace('*', '_').replace('/', '_')
    if digit_matcher.match(s) :
        s = '_' + s
    return s


def uniqueExpressionToCode(uniqueExpression, argumentValueCode):
    '''
    Turn the symbolic expression of a `kgprim.ct.metadata.UniqueExpression`
    into a string representing the same expression, suitable for use in code
    '''
    expression = uniqueExpression.expression
    toBeReplaced = expression.arg.symbol
    val = expression.expr.subs( {toBeReplaced: sympy.Symbol(name=argumentValueCode) } )
    return str(val)

def uniqueExpressionToIdentifier(uniqueExpression):
    return symbolicExpressionToIdentifier(uniqueExpression.expression)

#Monkey patch a type from the ct package

kgprim.ct.metadata.UniqueExpression.toCode = uniqueExpressionToCode
kgprim.ct.metadata.UniqueExpression.toIdentifier = uniqueExpressionToIdentifier


def foldConstants(transform):
    '''
    Replace the symbolic constants in the given transform with the corresponding
    floating point value.
    '''
    new_primitives = []
    modified = False
    for pct in transform.primitives :
        amount = pct.amount
        if isinstance(amount, numeric_argument.Expression) :
            if isinstance(amount.arg, numeric_argument.Constant) :
                ms = copy.copy(pct.motion)
                ms.amount = amount.arg.value
                new_primitives.append( kgprim.ct.models.PrimitiveCTransform(ms, pct.polarity) )
                modified = True
            else :
                new_primitives.append(pct)
    if modified :
        return kgprim.ct.models.CoordinateTransform(
            transform.leftFrame, transform.rightFrame, new_primitives)
    else :
        # nothing was changed, return the original object
        return transform


def floatLiteralsAsConstants(transform):
    '''
    Replace the floating point coefficients of the given transform with
    symbolic constants.
    '''
    new_primitives = []
    modified = False
    count = 0
    for pct in transform.primitives :
        amount = pct.amount
        if isinstance(amount, numbers.Real):
            ms = copy.copy(pct.motion)
            constant = numeric_argument.Constant('c{0}'.format(count), amount)
            ms.amount= numeric_argument.Expression(argument=constant)
            new_primitives.append( kgprim.ct.models.PrimitiveCTransform(ms, pct.polarity) )
            modified = True
            count = count + 1
        else :
            new_primitives.append(pct)
    if modified :
        return kgprim.ct.models.CoordinateTransform(
            transform.leftFrame, transform.rightFrame, new_primitives)
    else :
        # nothing was changed, return the original object
        return transform


class StatementsGenerator:
    '''
    Helper class to generate some common code statements related to a model and
    individual transforms (i.e. matrices).
    '''

    def __init__(self, aCodeGenerator):
        '''
        The argument `aCodeGenerator` is a configuration object. Its fields
        `langSpecifics`, `variableAccess`, `parameterAccess`, `constantAccess`
        encapsulate the details of a specific code-generation backend.

        TODO document the expected API of these objects
        '''
        self.lang      = aCodeGenerator.langSpecifics
        self.varAccess = aCodeGenerator.variableAccess
        self.parAccess = aCodeGenerator.parameterAccess
        self.cnstAccess= aCodeGenerator.constantAccess

    def getMatrixSpecificGenerators(self, matrixMetadata):
        resolved = self._resolveSymbols(matrixMetadata)
        def constantCoefficientsAssignments( indexableVariable):
            for row, col in matrixMetadata.constantCoefficients :
                value = resolved[row, col]
                if value != 0.0 : # we do not generate assignments of zeros, assuming the matrix is initialized
                    yield self.lang.matrixAssignment(indexableVariable, row, col, value.__str__())

        def variableCoefficientsAssignments(indexableVariable):
            for r,c in matrixMetadata.variableCoefficients :
                yield self.lang.matrixAssignment(indexableVariable, r,c, resolved[r,c].__str__())

        return {
            'constantCoefficientsAssignments' : constantCoefficientsAssignments,
            'variableCoefficientsAssignments' : variableCoefficientsAssignments
        }


    def _resolveSymbols(self, matrixMetadata):
        # A slightly hacky way of replacing expressions with code
        # that would resolve to the value.
        # We replace the sine/cosine of any symbol representing a rotation, and
        # the symbol itself for a translation.
        # The hacky way is to replace the expression with a new symbol whose
        # _name_ is equal to the code corresponding to the expression. This way
        # a "toString" would do the job.
        # The actual code used for the replacement is queried to the backend-
        # specific objects

        ctMeta = matrixMetadata.ctMetadata

        replacements = {}
        for var, expressions in ctMeta.vars.items() :
            for expr in expressions :
                symbol = expr.symbolicExpr
                if expr.isRotation() :
                    replacements[ sympy.sin(symbol) ] = sympy.Symbol( name=self.varAccess.sineValueExpression(expr) )
                    replacements[ sympy.cos(symbol) ] = sympy.Symbol( name=self.varAccess.cosineValueExpression(expr) )
                else :
                    replacements[ symbol ] = sympy.Symbol( name=self.varAccess.valueExpression(expr) )

        for par, expressions in ctMeta.pars.items() :
            for expr in expressions :
                symbol = expr.symbolicExpr
                if expr.isRotation() :
                    replacements[ sympy.sin(symbol) ] = sympy.Symbol( name=self.parAccess.sineValueExpression(expr)  )
                    replacements[ sympy.cos(symbol) ] = sympy.Symbol( name=self.parAccess.cosineValueExpression(expr))
                else :
                    replacements[ symbol ] = sympy.Symbol( name=self.parAccess.valueExpression(expr) )

        for cc, expressions in ctMeta.consts.items() :
            for expr in expressions :
                symbol = expr.symbolicExpr
                if expr.isRotation() :
                    replacements[ sympy.sin(symbol) ] = sympy.Symbol( name=self.cnstAccess.sineValueExpression(expr)  )
                    replacements[ sympy.cos(symbol) ] = sympy.Symbol( name=self.cnstAccess.cosineValueExpression(expr))
                else :
                    replacements[ symbol ] = sympy.Symbol( name=self.cnstAccess.valueExpression(expr) )

        return matrixMetadata.mx.subs( replacements )  # Sympy replacement


    def constantsDefinitions(self, constantsDict):
        '''
        A helper function to generate code that defines a list of variables
        initialized to the value of the constant expressions used by a model.

        This function does _not_ generate variables for the constants themselves,
        but only for the simple expressions involving the constants, like
        '2*c1' or 'c2/3'.

        The generated code depends on the language-specifics object this
        instance was created with.
        '''
        listing = []
        for constant, expressions_metadata in constantsDict.items() :
            cc_var = self.lang.constantValueCodeExpression(constant)
            for expr in expressions_metadata :
                expr_code = expr.toCode( cc_var )
                if expr.isRotation() :
                    var_name = self.lang.cachedSinValueIdentifier(expr)
                    value = '{sin}({arg})'.format(
                        sin = self.lang.sin_func(), arg = expr_code )
                    code = self.lang.constant_value_definition( var_name, value )
                    listing.append( code )
                    var_name = self.lang.cachedCosValueIdentifier(expr)
                    value = '{cos}({arg})'.format(
                        cos = self.lang.cos_func(), arg = expr_code )
                    code = self.lang.constant_value_definition( var_name, value )
                    listing.append( code )
                else:
                    # If the expression is the identity, we do not want to generate code
                    # for it, because we expect the constant itself to be
                    # defined elsewhere.
                    if not expr.isIdentity() :
                        var_name = self.lang.cachedValueIdentifier(expr)
                        listing.append( self.lang.constant_value_definition( var_name, expr_code ) )
        return listing

