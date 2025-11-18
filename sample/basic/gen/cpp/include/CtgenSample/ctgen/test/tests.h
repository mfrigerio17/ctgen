#pragma once

#include <iit/rbd/rbd.h>
#include <ctgen/cppiitrbd/dataset.h>

#include <CtgenSample/ctgen/transforms.h>

namespace CtgenSample {
namespace ctgen {

using Mx44 = iit::rbd::PlainMatrix<double,4,4>;


struct Test_frameA_X_frameB
{
    static void computeMatrix(::ctgen::TextDataset& ds, Mx44& computed);
    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed);
};

struct Test_frameD_X_frameB
{
    static void computeMatrix(::ctgen::TextDataset& ds, Mx44& computed);
    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed);
};

struct Test_frameE_X_frameG
{
    static void computeMatrix(::ctgen::TextDataset& ds, Mx44& computed);
    static void computeMatrix(::ctgen::NaiveBinDataset& ds, Mx44& computed);
};


}
}
