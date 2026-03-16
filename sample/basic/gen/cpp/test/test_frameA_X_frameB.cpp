#include <array>
#include <iit/rbd/rbd.h>
#include <ctgen/cppiitrbd/testmain_tpl.h>
#include <ctgen/cppiitrbd/dataset.h>

#include <CtgenSample/ctgen/transforms.h>

struct Test_frameA_X_frameB
{
    using Mx44 = iit::rbd::PlainMatrix<double,4,4>;

    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed) {
        compute_frameA_X_frameB<::ctgen::NaiveBinDataset>(ds, computed);
    }
    static void computeMatrix(::ctgen::TextDataset& ds, Mx44& computed) {
        compute_frameA_X_frameB<::ctgen::TextDataset>(ds, computed);
    }

private:
    template<class Dataset>
    static void compute_frameA_X_frameB(Dataset& ds, Mx44& computed)
    {
        using Transform = CtgenSample::ctgen::frameA_X_frameB;
        static Transform xt;
        computed = xt.frameA_XH_frameB().matrix();
    }

};


int main(int argc, char** argv)
{
    return ::ctgen::testmain<Test_frameA_X_frameB>(argc, argv);
}
