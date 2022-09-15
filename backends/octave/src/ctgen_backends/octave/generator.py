import logging, os
import lupa
import ctgen.common as ctgen_common
from kgprim.ct.repr.mxrepr import MatrixRepresentation

logger = logging.getLogger(__name__)

lua = lupa.LuaRuntime(unpack_returned_tuples=True)

luaCodeSrc = open( os.path.join(os.path.dirname(ctgen_common.__file__), "common.lua"), "r")
lua.execute(luaCodeSrc.read())
luaCodeSrc.close()




class LangSpecifics:
    def __init__(self, textgen_cfg):
        self.lua_cfg = textgen_cfg

    def matrixAssignment(self, subscriptableVariable,r,c,value):
        return "{var}({row},{col}) = {value}".format(var=subscriptableVariable, row=r+1, col=c+1, value=value)


class VariableAccess:
    def __init__(self, textgen_cfg):
        self.cfg = textgen_cfg
    def valueExpression(self, expr):
        return expr.toCode( self.cfg.variables.value_expression(expr.expression.arg) )
    def sineValueExpression(self, expr):
        return self.cfg.internal.cached_sinvalue_identifier(expr)
    def cosineValueExpression(self, expr):
        return self.cfg.internal.cached_cosvalue_identifier(expr)



class ParameterAccess:
    def __init__(self, textgen_cfg):
        self.cfg = textgen_cfg
        self.valuExprTpl = (textgen_cfg.this_obj_ref +
                '.' + textgen_cfg.parameters.member_name +
                '.{field}')

    def valueExpression(self, expr):
        return self.valuExprTpl.format(field=self.cfg.internal.cached_value_identifier(expr))
    def sineValueExpression(self, expr):
        return self.valuExprTpl.format(field=self.cfg.internal.cached_sinvalue_identifier(expr))
    def cosineValueExpression(self, expr):
        return self.valuExprTpl.format(field=self.cfg.internal.cached_cosvalue_identifier(expr))

class ConstantAccess:
    def __init__(self, cc_name, textgen_cfg):
        self.cfg = textgen_cfg
        self.cc_name = cc_name

    def valueExpression(self, expr):
        return self.cc_name + '.' + self.cfg.internal.cached_value_identifier(expr)
    def sineValueExpression(self, expr):
        return self.cc_name + '.' + self.cfg.internal.cached_sinvalue_identifier(expr)
    def cosineValueExpression(self, expr):
        return self.cc_name + '.' + self.cfg.internal.cached_cosvalue_identifier(expr)


class Generator:
    def __init__(self, configurator):
        basedir = os.path.dirname(__file__)
        luaCodeSrc = open( os.path.join(basedir, "tests_tpl.lua"), "r")
        lua.execute(luaCodeSrc.read()) # loads a global
        luaCodeSrc.close()
        luaCodeSrc = open( os.path.join(basedir, "generator.lua"), "r")
        self.luaGeneratorsF = lua.execute(luaCodeSrc.read())
        luaCodeSrc.close()
        self.config  = configurator

        textgen_cfg = configurator.getTextGeneratorsConfiguration()
        constants_container_name = textgen_cfg.constants.container_name(configurator.ctModel)

        self.variableAccess  = VariableAccess(textgen_cfg)
        self.parameterAccess = ParameterAccess(textgen_cfg)
        self.constantAccess  = ConstantAccess(constants_container_name, textgen_cfg)
        self.langSpecifics   = LangSpecifics(textgen_cfg)
        self.textgen_cfg = textgen_cfg

        self.statementsGenerator = ctgen_common.StatementsGenerator(self)


    def _generate_code(self, ctModelMetadata, matricesMetadata):
        '''
        Returns a dictionary of dictionaries of the same shape as the given
        `matricesMetadata`: the outer dictionary is indexed with a
        `MatrixRepresentation` value, and it has as many values as the given
        `matricesMetadata`. The inner dictionary is indexed by the name of a
        transform. Any value of the nested dictionaries is a tuple with a
        boolean success flag and the generated code.
        This function returns a second value, which is itself a tuple, with
        the success flag and the generated code for the model constants.
        '''
        if not self._consistentArgs(ctModelMetadata) :
            return None
        self.luaGen = self.luaGeneratorsF(ctModelMetadata, self.statementsGenerator, self.textgen_cfg)

        ret = {}
        for repr in matricesMetadata.keys() :
            mxsMeta = matricesMetadata[repr]
            code = {}
            for mxName in mxsMeta.keys() :
                mxMeta = mxsMeta[mxName]
                ok, codeOrError = self.luaGen.matrixFunction(mxMeta)
                self._logerr(ok, codeOrError, ctModelMetadata.name, mxMeta.ctMetadata.name)
                code[mxName] = (ok, codeOrError)
            ret[repr] = code

        ok, codeOrError = self.luaGen.modelConstants()
        if not ok :
            logger.error("Code generation of the constants of model '{0}' failed: {1}".format(ctModelMetadata.name, codeOrError))

        okt = False
        testscode = ""
        if MatrixRepresentation.homogeneous in matricesMetadata.keys():
            okt, testscode = self.luaGen.tests(matricesMetadata[MatrixRepresentation.homogeneous])
            if not okt :
                logger.error("Code generation of the tests of model '{0}' failed: {1}".format(ctModelMetadata.name, testscode))
        else :
            errmsg = "Test generation only available for homogeneous transforms"
            logger.warning(errmsg)
            okt = False
            testscode = errmsg

        return ret, (ok, codeOrError), (okt, testscode)


    def generate(self, ctModelMetadata, matricesMetadata):
        if not self._consistentArgs(ctModelMetadata) :
            return None

        allCode, constants, tests = self._generate_code(ctModelMetadata, matricesMetadata)

        odir = self.config.getOutputDirectory()
        def fwrite(ok, filename, text) :
            fpath = os.path.join(odir, filename)
            if ok :
                f = open(fpath, 'w')
                f.write(text)
                f.close()
            else :
                logger.info("Skipping file '{f}', as code generation failed".format(f=fpath))


        for repr in allCode.keys() :
            mxsMeta = matricesMetadata[repr]
            codeDict= allCode[repr]
            for mxName in mxsMeta.keys() :
                mxMeta  = mxsMeta[mxName]
                ok,codeOrError = codeDict[mxName]
                filename = self.config.getClassName(mxMeta) + ".m"
                fwrite(ok, filename, codeOrError)

        ok, codeOrError = constants[:]
        filename = self.textgen_cfg.constants.container_name(ctModelMetadata) + "_init.m"
        fwrite(ok, filename, codeOrError)

        ok, codeOrError = tests[:]
        fwrite(ok, "tests.m", codeOrError)

    def _logerr(self, ok, errmsg, model, tr ):
        if not ok :
            logger.error("Code generation failed - model '{model}', transform '{tr}': {err}"
                         .format(model=model, tr=tr, err=errmsg) )

    def _consistentArgs(self, ctModelMetadata):
        abort = False
        if self.config is None :
            logger.error("Configurator not set. Aborting")
            abort = True
        if self.config.ctModel != ctModelMetadata.ctModel :
             logger.warning("The coordinate transform model of the given metadata object does not match the one used to configure this generator")
             #abort = True
        #TODO more?
        if abort :
            logger.error("Inconsistent arguments - aborting")
        return not abort



