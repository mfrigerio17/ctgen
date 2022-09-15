local common = common

local testall_tpl =
[[
«modelConstantsGlobal»_init;

@for i, mxmeta in ipairs(matrices_metadata) do
tf = «ids.mxClassName(mxmeta)»();
ds = BinDataset('dataset_«mxmeta.ctMetadata.name».bin');
display("Testing matrix «mxmeta.ctMetadata.name» . . .");
ds.testMatrix(tf, «common.pylen(mxmeta.ctMetadata.vars)»);
display("");

@end
]]

local function generator(env)
    local function actual(matrices_metadata)
        local matrices = {}
        for key in python.iter(matrices_metadata) do
            table.insert(matrices, matrices_metadata[key])
        end
        env.matrices_metadata = matrices
        return common.tpleval(testall_tpl, env)
    end
    return actual
end


tests_generator = generator