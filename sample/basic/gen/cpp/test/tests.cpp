#include <CtgenSample/ctgen/test/tests.h>

template<int N>
using Vec = iit::rbd::PlainMatrix<double,N,1>;

CtgenSample::ctgen::Transforms transforms;
CtgenSample::ctgen::VarsState q;
CtgenSample::ctgen::ModelParameters params;

namespace {

template<class Dataset>
void compute_frameA_X_frameB(Dataset& ds, CtgenSample::ctgen::Mx44& computed)
{
    computed = transforms.m_frameA_X_frameB(q).frameA_XH_frameB().matrix();
}

template<class Dataset>
void compute_frameD_X_frameB(Dataset& ds, CtgenSample::ctgen::Mx44& computed)
{
    Vec<2> aux_pars;
    ds.readVector(2, aux_pars);
    params.my_rot = aux_pars[0];
    params.my_tr = aux_pars[1];
    transforms.updateParams(params);
    computed = transforms.m_frameD_X_frameB(q).frameD_XH_frameB().matrix();
}

template<class Dataset>
void compute_frameE_X_frameG(Dataset& ds, CtgenSample::ctgen::Mx44& computed)
{
    Vec<3> aux_vars;
    ds.readVector(3, aux_vars);
    q.q0 = aux_vars(0);
    q.q1 = aux_vars(1);
    q.q2 = aux_vars(2);
    computed = transforms.m_frameE_X_frameG(q).frameE_XH_frameG().matrix();
}


}

void CtgenSample::ctgen::Test_frameA_X_frameB::computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed) {
    compute_frameA_X_frameB<::ctgen::NaiveBinDataset>(ds, computed);
}
void CtgenSample::ctgen::Test_frameA_X_frameB::computeMatrix(::ctgen::TextDataset& ds, Mx44& computed) {
    compute_frameA_X_frameB<::ctgen::TextDataset>(ds, computed);
}

void CtgenSample::ctgen::Test_frameD_X_frameB::computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed) {
    compute_frameD_X_frameB<::ctgen::NaiveBinDataset>(ds, computed);
}
void CtgenSample::ctgen::Test_frameD_X_frameB::computeMatrix(::ctgen::TextDataset& ds, Mx44& computed) {
    compute_frameD_X_frameB<::ctgen::TextDataset>(ds, computed);
}

void CtgenSample::ctgen::Test_frameE_X_frameG::computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed) {
    compute_frameE_X_frameG<::ctgen::NaiveBinDataset>(ds, computed);
}
void CtgenSample::ctgen::Test_frameE_X_frameG::computeMatrix(::ctgen::TextDataset& ds, Mx44& computed) {
    compute_frameE_X_frameG<::ctgen::TextDataset>(ds, computed);
}


