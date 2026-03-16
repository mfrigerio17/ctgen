#include <array>
#include <iit/rbd/rbd.h>
#include <ctgen/cppiitrbd/testmain_tpl.h>
#include <ctgen/cppiitrbd/dataset.h>

#include <CtgenSample/ctgen/transforms.h>

struct Test_frameD_X_frameB
{
    using Mx44 = iit::rbd::PlainMatrix<double,4,4>;

    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed) {
        compute_frameD_X_frameB<::ctgen::NaiveBinDataset>(ds, computed);
    }
    static void computeMatrix(::ctgen::TextDataset& ds, Mx44& computed) {
        compute_frameD_X_frameB<::ctgen::TextDataset>(ds, computed);
    }

private:
    template<class Dataset>
    static void compute_frameD_X_frameB(Dataset& ds, Mx44& computed)
    {
        using Transform = CtgenSample::ctgen::frameD_X_frameB;
        using SrcParams = CtgenSample::ctgen::ModelParameters;
        using Params    = CtgenSample::ctgen::Parameters;
        static Params params;
        static Transform xt(params);
        static SrcParams srcParams;
        std::array<double, 2> aux_pars;
        ds.readVector(2, aux_pars);
        srcParams.my_rot = aux_pars[0];
        srcParams.my_tr = aux_pars[1];
    // inject the new parameter values in the transform
        params = srcParams;
        xt.update();
        computed = xt.frameD_XH_frameB().matrix();
    }

};


int main(int argc, char** argv)
{
    return ::ctgen::testmain<Test_frameD_X_frameB>(argc, argv);
}
