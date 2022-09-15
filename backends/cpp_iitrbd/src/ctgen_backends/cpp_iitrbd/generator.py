import os, logging
import lupa
from kgprim.ct.repr.mxrepr import MatrixRepresentation
import ctgen.common as ctgen_common

logger = logging.getLogger(__name__)

lua = lupa.LuaRuntime(unpack_returned_tuples=True)

def __luaExec(sourcefile) :
    luaCodeSrc = open( sourcefile, "r")
    luaret = lua.execute(luaCodeSrc.read())
    luaCodeSrc.close()
    return luaret

__dirhere = os.path.dirname(__file__)

__luaExec( os.path.join( os.path.dirname(ctgen_common.__file__), "common.lua") )

__luaExec( os.path.join(__dirhere, "header_tpl.lua") )
__luaExec( os.path.join(__dirhere, "source_tpl.lua") )
__luaExec( os.path.join(__dirhere, "tests_tpl.lua") )
__luaExec( os.path.join(__dirhere, "cmake_tpl.lua") )
lua_gen = __luaExec( os.path.join(__dirhere, "generator.lua") )




class CppBackendSpecifics:
    def __init__(self, lua_codegen_cfg):
        self.lua_cfg       = lua_codegen_cfg
        self.scalar_t      = self.lua_cfg.internal.scalar_t
        self.scalar_traits = self.lua_cfg.scalar_traits.type_name
        self.constantValueCodeExpression = lua_codegen_cfg.constants.value_expression

    def sin_func(self):
        return self.scalar_traits + '::sin'
    def cos_func(self):
        return self.scalar_traits + '::cos'

    def constant_value_definition(self, varname, varvalue):
        return '{const} {typ} {name} = {value};'.format(
            const = self.lua_cfg.const_var_modifier,
            typ  = self.scalar_t,
            name = varname,
            value= varvalue
        )

    def cachedValueIdentifier(self, expression):
        return self.lua_cfg.internal.cached_value_identifier(expression)
    def cachedSinValueIdentifier(self, expression):
        return self.lua_cfg.internal.cached_sinvalue_identifier(expression)
    def cachedCosValueIdentifier(self, expression):
        return self.lua_cfg.internal.cached_cosvalue_identifier(expression)

    def matrixAssignment(self, subscriptableVariable,r,c,value):
        field_rot_mx = self.lua_cfg.external.iit_rbd.inherited_members.ct.rot_mx
        field_tr_vect= self.lua_cfg.external.iit_rbd.inherited_members.ct.vector
        if c<3 : # the rotation matrix
            return "{var}.{mx}({row},{col}) = {value};".format(var=subscriptableVariable, mx=field_rot_mx, row=r, col=c, value=value)
        else : # the translation vector
            if r<3 :
                return "{var}.{tr}({row}) = {value};".format(var=subscriptableVariable, tr=field_tr_vect, row=r, value=value)
        return ""


class VariableAccess:
    def __init__(self, textgen_cfg):
        self.textgen_cfg = textgen_cfg

    def valueExpression(self, expr):
        return expr.toCode( self.textgen_cfg.variables.value_expression(expr.expression.arg) )
    def sineValueExpression(self, expr):
        return self.textgen_cfg.internal.cached_sinvalue_identifier(expr)
    def cosineValueExpression(self, expr):
        return self.textgen_cfg.internal.cached_cosvalue_identifier(expr)


class ParameterAccess:
    def __init__(self, textgen_cfg):
        self.cfg = textgen_cfg.internal
        self.valuExprTpl = textgen_cfg.transform_class.members.parameters + '.{field}'

    def valueExpression(self, expr):
        return self.valuExprTpl.format(field=self.cfg.cached_value_identifier(expr))
    def sineValueExpression(self, expr):
        return self.valuExprTpl.format(field=self.cfg.cached_sinvalue_identifier(expr))
    def cosineValueExpression(self, expr):
        return self.valuExprTpl.format(field=self.cfg.cached_cosvalue_identifier(expr))

class ConstantAccess:
    def __init__(self, textGenerationConfiguration):
        self.cfg = textGenerationConfiguration
        self.expr_container = self.cfg.internal.constants_container

    def valueExpression(self, expr):
        if expr.isIdentity() :
            constant = expr.expression.arg
            if self.cfg.constants.generate_local_defs :
                # conform to the policy of my generators
                cont = self.cfg.constants.local_defs_container_name
                return cont+'::'+self.cfg.model_property_to_varname(constant)
            else :
                # use the user-supplied read-access expression
                return self.cfg.constants.value_expression(constant)
        else :
            return self.expr_container + '::' +\
                self.cfg.internal.cached_value_identifier(expr)

    def sineValueExpression(self, expr):
        return  self.expr_container + '::' +\
            self.cfg.internal.cached_sinvalue_identifier(expr)
    def cosineValueExpression(self, expr):
        return  self.expr_container + '::' +\
            self.cfg.internal.cached_cosvalue_identifier(expr)


class Generator:
    def __init__(self, config):
        self.config = config
        self.lua_codegen_cfg = config.getTextGeneratorsConfiguration()

        self.variableAccess  = VariableAccess(self.lua_codegen_cfg)
        self.parameterAccess = ParameterAccess(self.lua_codegen_cfg)
        self.constantAccess  = ConstantAccess(self.lua_codegen_cfg)
        self.langSpecifics   = CppBackendSpecifics(self.lua_codegen_cfg )

        self.statementsGenerators = ctgen_common.StatementsGenerator(self)


    def generate_code(self, ctModelMetadata, matricesMetadata):
        mxMetadata = None
        if MatrixRepresentation.homogeneous in matricesMetadata:
            mxMetadata = matricesMetadata[MatrixRepresentation.homogeneous]
        else :
            logger.error("This generator requires the metadata for the homogeneous coordinate representation of the transformation matrices")
            return (False,''), (False,'')

        generators = lua_gen.generators(ctModelMetadata, mxMetadata, self.statementsGenerators, self.lua_codegen_cfg)
        self.generators = generators

        okh, headerCode = generators.headerFileCode()
        if not okh :
            logger.error("Header code generation for model '{0}' failed: {1}".format(ctModelMetadata.name, headerCode))

        oks, sourceCode = generators.sourceFileCode()
        if not oks :
            logger.error("Source code generation for model '{0}' failed: {1}".format(ctModelMetadata.name, sourceCode))

        return (okh,headerCode), (oks,sourceCode)


    def generate(self, ctModelMetadata, matricesMetadata):
        outputDir = self.config.getOutputDirectory()
        def write_file(code, filepath):
            fpath = os.path.join( outputDir, filepath )
            f = open(fpath, 'w')
            f.write(code)
            f.close()

        fileNames = self.config.getOutputFileNames()
        #implext = '.h' if self.config.generateTemplates() else '.cpp'

        hpath = self.config.getHeadersPath()
        fullhpath = os.path.join(outputDir, hpath)
        if not os.path.exists(fullhpath):  # create it if it is not there
            os.makedirs(fullhpath)

        (okh,header), (oks,source) = self.generate_code(ctModelMetadata, matricesMetadata)
        if okh :
            write_file(header, os.path.join(hpath, fileNames.header) )
        if oks :
            fname = fileNames.source
            if self.config.generateTemplates() :
                fname = os.path.join(hpath, fname + ".h")
            write_file(source, fname)

        if (not okh) or (not oks) :
            return

        ok, code = self.generators.main()
        if not ok :
            logger.error("Failed to generate sample main file: " + code)
        else:
            write_file(code, 'main.cpp')

        # tests
        testsdir = fileNames.test.subdir
        # the test subdirectory for the sources
        fulldir = os.path.join( outputDir, testsdir )
        if not os.path.exists(fulldir) :
            os.makedirs(fulldir)
        # and now for the header file
        fulldir = os.path.join( fullhpath, testsdir )
        if not os.path.exists(fulldir) :
            os.makedirs(fulldir)

        ok, code = self.generators.tests.header()
        if not ok :
            logger.error("Failed to generate tests header: " + code)
        else:
            hpath_test = os.path.join(hpath, testsdir)
            write_file(code, os.path.join(hpath_test, fileNames.test.header))

        ok, code = self.generators.tests.source()
        if not ok :
            logger.error("Failed to generate tests source: " + code)
        else:
            write_file(code, os.path.join(testsdir, fileNames.test.source))

        for tf in ctModelMetadata.transformsMetadata :
            ok, code = self.generators.tests.per_tf_main(tf)
            if not ok :
                logger.error("Failed to generate test file: " + code)
            else:
                write_file(code, os.path.join(testsdir, fileNames.test.per_tf_source(tf)))

        ok, code = self.generators.cmake()
        if not ok :
            logger.error("Failed to generate cmake file: " + code)
        else:
            write_file(code, "CMakeLists.txt")