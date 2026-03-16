#include <array>
#include <iit/rbd/rbd.h>
#include <ctgen/cppiitrbd/testmain_tpl.h>
#include <ctgen/cppiitrbd/dataset.h>

#include <CtgenSample/ctgen/transforms.h>

struct Test_frameE_X_frameG
{
    using Mx44 = iit::rbd::PlainMatrix<double,4,4>;

    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed) {
        compute_frameE_X_frameG<::ctgen::NaiveBinDataset>(ds, computed);
    }
    static void computeMatrix(::ctgen::TextDataset& ds, Mx44& computed) {
        compute_frameE_X_frameG<::ctgen::TextDataset>(ds, computed);
    }

private:
    template<class Dataset>
    static void compute_frameE_X_frameG(Dataset& ds, Mx44& computed)
    {
        using Transform = CtgenSample::ctgen::frameE_X_frameG;
        static Transform xt;
        static CtgenSample::ctgen::VarsState q;
        std::array<double, 3> aux_vars;
        ds.readVector(3, aux_vars);
        q.q0 = aux_vars[0];
        q.q1 = aux_vars[1];
        q.q2 = aux_vars[2];
        computed = xt(q).frameE_XH_frameG().matrix();
    }

};


int main(int argc, char** argv)
{
    return ::ctgen::testmain<Test_frameE_X_frameG>(argc, argv);
}
