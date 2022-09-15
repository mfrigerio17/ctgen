This is a C++ backend for the `ctgen` tool.
Use the switch `--lang cpp_iitrbd` to use it.

# Dependencies
The generated C++ code depends on a few header files from the
[iit-rbd](web-iitrbd) library, which in turn depens on [Eigen](web-eigen).

# Generated code
A type (class) is generated for every desired transform in the input model.
The class interface allows to retrieve the different matrix representations of
the same transform, as well as the different polarities.

The following code snippets illustrate the API of the generated code.
They refer to the code generated from the sample model distributed with
`ctgen`. The snippets are extracted from the [`usage.cpp`](sample/usage.cpp)
sample file.

```c++
    using namespace CtgenSample::ctgen;
    //...

    frameA_X_frameB AB;         // the transform object

    iit::rbd::Vector3d v;
    AB.frameA_XH_frameB() * v;  // homogeneous (H) transform from B to A coordinates
    AB.frameB_XH_frameA() * v;  // opposite polarity, i.e., from A to B
```
Note that it is not needed to use 4-coordinate vectors with the homogeneous
transforms. In fact, one _has_ to use 3-coordinate vectors.

The `matrix()` method allows to get the matrix in explicit form:

```c++
    using Matrix44 = iit::rbd::PlainMatrix<double,4,4>;
    using Matrix66 = iit::rbd::Matrix66d;

    Matrix44 A_XH_B = AB.frameA_XH_frameB().matrix(); // 4x4 homogeneous coordinates
    Matrix66 B_XM_A = AB.frameB_XM_frameA().matrix(); // 6x6 spatial coordinates (velocity)
```

## Container
We also generate a class containing all the desired transforms from your input
model. This is useful to update all the transforms at the same time (with
variables and/or parameters - see below).

```c++
    Transforms tfs;    // the container object
                       // Some public members are the transforms objects:

    frameA_X_frameB & ABref = tfs.m_frameA_X_frameB;
    frameD_X_frameB & DBref = tfs.m_frameD_X_frameB;
    frameE_X_frameG & EGref = tfs.m_frameE_X_frameG;
```

## Variables
If any transform in your model depends on one or more variables, a
variables-status type will be generated. An instance of such type can be used
to update the transform:

```c++
    VarsState vs;   //
    vs.q0 = 0;      // there are three variables in the sample model
    vs.q1 = 0;
    vs.q2 = 0;

    frameE_X_frameG EG;            // a non-constant transform
    EG(vs);                        // set the variable state via operator()
    vs.q0 = 0.5;
    vs.q1 = 0.3;
    EG(vs).frameE_XH_frameG() * v; // can use the other methods in sequence
```

## Parameters
If any transform also depends on parameters, a type for the parameters values
will be generated. The container object allows to update the parameters for all
the transforms:

```c++
    Transforms tfs;
    ModelParameters ps;
    ps.my_rot = 1.1; // a rotation parameter of the sample model
    ps.my_tr  = 2;   // a translation parameter

    tfs.updateParams(ps); // the parameters are shared across all members

    VarsState vs;
    // vs.q0 = ...
    tfs.m_frameD_X_frameB(vs); // this update will reflect the new parameters
```

Note that setting the parameters will NOT update any transform right away. The
transforms will reflect the new parameters at the subsequent update with a new
variables state.

If you are not using the container object, things are a little bit more
complicated. A parametric transform requires a `Parameters` object at
construction time; updates must happen by assigning a `ModelParameters` object
to it:

```c++
    Parameters internal;           // do not modify the fields by hand
    frameD_X_frameB DXB(internal); // stores a reference to the parameters!
    // ...
    ps.my_rot = 0.17;
    ps.my_tr  = 1.2;
    internal = ps;           // updates the necessary values
    // ...
    VarsState vs;
    // vs.q0 = ...
    DXB(vs);                 // this update uses the new parameters
```


[web-iitrbd]: https://bitbucket.org/robcogendevs/iit-rbd/
[web-eigen]: https://eigen.tuxfamily.org
