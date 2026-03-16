#ifndef CTGENSAMPLE_TRANSFORMS_GEN_H
#define CTGENSAMPLE_TRANSFORMS_GEN_H

#include <iit/rbd/compact_transform.h>
#include <iit/rbd/scalar_traits.h>

namespace CtgenSample {
namespace ctgen {



using ScalarTraits = iit::rbd::DoubleTraits;
using scalar_t = typename ScalarTraits::Scalar;


/**
 * The numerical constants as they appear in the source model
 */
struct ModelConstants
{
    static constexpr scalar_t c0{0.2};
    static constexpr scalar_t c1{3.1};
    static constexpr scalar_t rz{0.6};
};

/**
 * Derived constant expressions
 */
struct Constants
{
    static constexpr scalar_t s__c0{ScalarTraits::sin(ModelConstants::c0)};
    static constexpr scalar_t c__c0{ScalarTraits::cos(ModelConstants::c0)};
    static constexpr scalar_t s__rz{ScalarTraits::sin(ModelConstants::rz)};
    static constexpr scalar_t c__rz{ScalarTraits::cos(ModelConstants::rz)};
};


struct ModelParameters
{
    scalar_t my_rot;
    scalar_t my_tr;
};


struct Parameters
{
    scalar_t s__my_rot;
    scalar_t c__my_rot;
    scalar_t my_tr_2;

    Parameters() {}
    explicit Parameters(const ModelParameters& params) {
        s__my_rot = ScalarTraits::sin( params.my_rot );
        c__my_rot = ScalarTraits::cos( params.my_rot );
        my_tr_2 = params.my_tr/2;

    }

    Parameters& operator=(const ModelParameters& params) {
        s__my_rot = ScalarTraits::sin( params.my_rot );
        c__my_rot = ScalarTraits::cos( params.my_rot );
        my_tr_2 = params.my_tr/2;

        return *this;
    }
};


struct VarsState {
    using Scalar = CtgenSample::ctgen::scalar_t; // required by the matrix infrastructure
    scalar_t q0;
    scalar_t q1;
    scalar_t q2;
};

using state_t = VarsState;

template<typename ACTUAL>
struct Transform : public iit::rbd::TransformBase<scalar_t>,
    public iit::rbd::StateDependentBase<state_t, ACTUAL>
{
    using Base = iit::rbd::TransformBase<scalar_t>;
    Transform() : Base(0) {} // calls explicit constructor setting data to 0
};

using A_XM_B = iit::rbd::A_XM_B< scalar_t >;
using B_XM_A = iit::rbd::B_XM_A< scalar_t >;
using A_XF_B = iit::rbd::A_XF_B< scalar_t >;
using B_XF_A = iit::rbd::B_XF_A< scalar_t >;
using A_XH_B = iit::rbd::A_XH_B< scalar_t >;
using B_XH_A = iit::rbd::B_XH_A< scalar_t >;


struct frameA_X_frameB : public Transform<frameA_X_frameB>
{
    frameA_X_frameB();
    const frameA_X_frameB& update(const state_t&) {
        return update();
    }
    const frameA_X_frameB& update();

    A_XM_B frameA_XM_frameB() const { return this->template as<A_XM_B>(); }
    B_XM_A frameB_XM_frameA() const { return this->template as<B_XM_A>(); }
    A_XF_B frameA_XF_frameB() const { return this->template as<A_XF_B>(); }
    B_XF_A frameB_XF_frameA() const { return this->template as<B_XF_A>(); }
    A_XH_B frameA_XH_frameB() const { return this->template as<A_XH_B>(); }
    B_XH_A frameB_XH_frameA() const { return this->template as<B_XH_A>(); }

};


struct frameD_X_frameB : public Transform<frameD_X_frameB>
{
    frameD_X_frameB(const Parameters& params);
    const frameD_X_frameB& update(const state_t&) {
        return update();
    }
    const frameD_X_frameB& update();

    A_XM_B frameD_XM_frameB() const { return this->template as<A_XM_B>(); }
    B_XM_A frameB_XM_frameD() const { return this->template as<B_XM_A>(); }
    A_XF_B frameD_XF_frameB() const { return this->template as<A_XF_B>(); }
    B_XF_A frameB_XF_frameD() const { return this->template as<B_XF_A>(); }
    A_XH_B frameD_XH_frameB() const { return this->template as<A_XH_B>(); }
    B_XH_A frameB_XH_frameD() const { return this->template as<B_XH_A>(); }

protected:
    const Parameters& parameters;
};


struct frameE_X_frameG : public Transform<frameE_X_frameG>
{
    frameE_X_frameG();
    const frameE_X_frameG& update(const state_t&);

    A_XM_B frameE_XM_frameG() const { return this->template as<A_XM_B>(); }
    B_XM_A frameG_XM_frameE() const { return this->template as<B_XM_A>(); }
    A_XF_B frameE_XF_frameG() const { return this->template as<A_XF_B>(); }
    B_XF_A frameG_XF_frameE() const { return this->template as<B_XF_A>(); }
    A_XH_B frameE_XH_frameG() const { return this->template as<A_XH_B>(); }
    B_XH_A frameG_XH_frameE() const { return this->template as<B_XH_A>(); }

};



struct Transforms
{
    Transforms();
    Transforms(const ModelParameters& initial);
    void updateParams(const ModelParameters& mp) {
        parameters = mp;
    }

    void update(const state_t&);

    frameA_X_frameB m_frameA_X_frameB;
    frameD_X_frameB m_frameD_X_frameB;
    frameE_X_frameG m_frameE_X_frameG;

protected:
    Parameters parameters;
};



}
}


#endif
