#include <iostream>
#include <iit/rbd/rbd.h>
#include "transforms.h"

/*
 * This sample program demonstrates the API of the generated C++ code.
 * It refers to the sample model distributed with the CTGen tool.
 */

using namespace CtgenSample::ctgen;

int main()
{
    frameA_X_frameB AB;         // a transform object

    iit::rbd::Vector3d v;
    AB.frameA_XH_frameB() * v;  // homogeneous transform from B to A coordinates
    AB.frameB_XH_frameA() * v;  // opposite polarity

    using Matrix44 = iit::rbd::PlainMatrix<double,4,4>;
    using Matrix66 = iit::rbd::Matrix66d;

    Matrix44 A_XH_B = AB.frameA_XH_frameB().matrix(); // 4x4 homogeneous coordinates
    Matrix66 B_XM_A = AB.frameB_XM_frameA().matrix(); // 6x6 spatial coordinates (velocity)


    VarsState vs;   //
    vs.q0 = 0;      // there are three variables in the sample model
    vs.q1 = 0;
    vs.q2 = 0;

    frameE_X_frameG EG;            // a non-constant transform
    EG(vs);                        // set the variable state via operator()
    vs.q0 = 0.5;
    vs.q1 = 0.3;
    EG(vs).frameE_XH_frameG() * v; // can use the other methods in sequence

    Transforms tfs;    // the container object
                       // Some public members are the transforms objects:

    frameA_X_frameB & ABref = tfs.m_frameA_X_frameB;
    frameD_X_frameB & DBref = tfs.m_frameD_X_frameB;
    frameE_X_frameG & EGref = tfs.m_frameE_X_frameG;


    ModelParameters ps;
    ps.my_rot = 1.1;
    ps.my_tr  = 2;

    tfs.updateParams(ps);      // the values are shared across all members
    tfs.m_frameD_X_frameB(vs); // the update will reflect the new parameters


    Parameters internal;           // do not modify the fields by hand
    frameD_X_frameB DXB(internal); // stores a reference to the parameters!
    ps.my_rot = 0.17;
    ps.my_tr  = 1.2;
    internal = ps;           // updates the necessary values
    DXB(vs);                 // this update uses the new parameters

    return 0;
}
