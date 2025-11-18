#include <CtgenSample/ctgen/transforms.h>

using CtgenSample::ctgen::scalar_t;

const scalar_t CtgenSample::ctgen::ModelConstants::c0{0.2};
const scalar_t CtgenSample::ctgen::ModelConstants::c1{3.1};
const scalar_t CtgenSample::ctgen::ModelConstants::rz{0.6};

const scalar_t CtgenSample::ctgen::Constants::s__c0{ScalarTraits::sin(ModelConstants::c0)};
const scalar_t CtgenSample::ctgen::Constants::c__c0{ScalarTraits::cos(ModelConstants::c0)};
const scalar_t CtgenSample::ctgen::Constants::s__rz{ScalarTraits::sin(ModelConstants::rz)};
const scalar_t CtgenSample::ctgen::Constants::c__rz{ScalarTraits::cos(ModelConstants::rz)};





CtgenSample::ctgen::frameA_X_frameB::frameA_X_frameB()
{
    this->ct.a_R_b(0,0) = 1;
    this->ct.a_R_b(0,1) = 0;
    this->ct.a_R_b(0,2) = 0;
    this->ct.r_ab_a(0) = 0;
    this->ct.a_R_b(1,0) = 0;
    this->ct.a_R_b(1,1) = Constants::c__c0;
    this->ct.a_R_b(1,2) = -Constants::s__c0;
    this->ct.r_ab_a(1) = Constants::c__c0*ModelConstants::c1;
    this->ct.a_R_b(2,0) = 0;
    this->ct.a_R_b(2,1) = Constants::s__c0;
    this->ct.a_R_b(2,2) = Constants::c__c0;
    this->ct.r_ab_a(2) = Constants::s__c0*ModelConstants::c1;
    
    
    
    
}


const typename CtgenSample::ctgen::frameA_X_frameB& CtgenSample::ctgen::frameA_X_frameB::update()
{

    return *this;
}



CtgenSample::ctgen::frameD_X_frameB::frameD_X_frameB(const Parameters& params)
    : parameters(params)
{
    this->ct.a_R_b(1,0) = -Constants::s__rz;
    this->ct.a_R_b(1,1) = Constants::c__rz;
    this->ct.a_R_b(1,2) = 0;
    this->ct.r_ab_a(1) = 0;
    
    
    
    
}


const typename CtgenSample::ctgen::frameD_X_frameB& CtgenSample::ctgen::frameD_X_frameB::update()
{

    this->ct.a_R_b(0,0) = -Constants::c__rz*parameters.s__my_rot;
    this->ct.a_R_b(0,1) = -Constants::s__rz*parameters.s__my_rot;
    this->ct.a_R_b(0,2) = -parameters.c__my_rot;
    this->ct.r_ab_a(0) = -parameters.c__my_rot*parameters.my_tr_2 + parameters.my_tr_2*parameters.s__my_rot;
    this->ct.a_R_b(2,0) = Constants::c__rz*parameters.c__my_rot;
    this->ct.a_R_b(2,1) = Constants::s__rz*parameters.c__my_rot;
    this->ct.a_R_b(2,2) = -parameters.s__my_rot;
    this->ct.r_ab_a(2) = -parameters.c__my_rot*parameters.my_tr_2 - parameters.my_tr_2*parameters.s__my_rot;
    return *this;
}



CtgenSample::ctgen::frameE_X_frameG::frameE_X_frameG()
{
    this->ct.a_R_b(0,1) = 0;
    
    
    
    
}


const typename CtgenSample::ctgen::frameE_X_frameG& CtgenSample::ctgen::frameE_X_frameG::update(const state_t& state)
{
    scalar_t s__q1 = ScalarTraits::sin( state.q1 );
    scalar_t c__q1 = ScalarTraits::cos( state.q1 );
    scalar_t s__q0 = ScalarTraits::sin( state.q0 );
    scalar_t c__q0 = ScalarTraits::cos( state.q0 );

    this->ct.a_R_b(0,0) = c__q1;
    this->ct.a_R_b(0,2) = s__q1;
    this->ct.r_ab_a(0) = s__q1*state.q2;
    this->ct.a_R_b(1,0) = s__q0*s__q1;
    this->ct.a_R_b(1,1) = c__q0;
    this->ct.a_R_b(1,2) = -c__q1*s__q0;
    this->ct.r_ab_a(1) = -c__q1*s__q0*state.q2;
    this->ct.a_R_b(2,0) = -c__q0*s__q1;
    this->ct.a_R_b(2,1) = s__q0;
    this->ct.a_R_b(2,2) = c__q0*c__q1;
    this->ct.r_ab_a(2) = c__q0*c__q1*state.q2;
    return *this;
}





CtgenSample::ctgen::Transforms::Transforms(const ModelParameters& initial) :
m_frameA_X_frameB(),m_frameD_X_frameB(parameters),m_frameE_X_frameG(), parameters(initial)
{}

CtgenSample::ctgen::Transforms::Transforms() :
m_frameA_X_frameB(),m_frameD_X_frameB(parameters),m_frameE_X_frameG(), parameters(/*do we want the default instance of ModelParameters ?*/)
{}



void CtgenSample::ctgen::Transforms::update(const state_t& state)
{
    m_frameA_X_frameB.update(state);
    m_frameD_X_frameB.update(state);
    m_frameE_X_frameG.update(state);
}



