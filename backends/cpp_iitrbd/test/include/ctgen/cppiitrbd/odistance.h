#ifndef CTGEN_CPP_IITRBD_BACKEND_TESTING_ODISTANCE_H
#define CTGEN_CPP_IITRBD_BACKEND_TESTING_ODISTANCE_H

#include <iit/rbd/rbd.h>
#include <cassert>

namespace ctgen {

using vector3_t = iit::rbd::Vector3d;
using matrix33_t= iit::rbd::Matrix33d;

struct AxisAngle {
	vector3_t axis;
	double    angle;
	AxisAngle() : axis(vector3_t(1.0,0.0,0.0)), angle(0.0) {}
	AxisAngle(const vector3_t& a, double th) : axis(a/a.norm()), angle(th) {}
	vector3_t omega() { return axis*angle; }
};

/**
 * The difference between two rotation matrices, as an axis-angle.
 *
 * \return the rotation required to go from the second to the first argument,
 * that is, the first "minus" the second.
 */
template<typename D1, typename D2>
AxisAngle orientationDistance(const D1& _R_desired, const D2& _R_actual)
{
    using iit::rbd::X;
    using iit::rbd::Y;
    using iit::rbd::Z;
    static constexpr double thresh = 1e-6;//TODO #magic-number
    //TODO compile time checks on the size, although the following already fails if they are not 3x3
    matrix33_t R = _R_actual.transpose() * _R_desired; // this is 'actual_R_desired'
    double trace = R.trace();
    // R is a rotation matrix, the max abs value of the trace is 3; if it is
    // larger, it is because of numerical errors
    trace = trace>3? 3 : (trace<-3? -3 : trace);

    double x = R(Z,Y) - R(Y,Z);
    double y = R(X,Z) - R(Z,X);
    double z = R(Y,X) - R(X,Y);
    double norm = sqrt(x*x + y*y + z*z);
    if(norm < thresh) {
        // the norm of the axis is 0, either a 0 or PI rotation
        // for the return, we arbitrarily choose the (0,0,1) axis

        double th = std::acos( (trace-1)/2 );
        assert( ((std::abs(th - M_PI)<1e-3) or (std::abs(th)<1e-3)) );
        return AxisAngle(vector3_t(0.0, 0.0, 1.0), th);
    }
    double theta = atan2( norm, trace-1 );

    return AxisAngle(vector3_t(x/norm, y/norm, z/norm), theta);
    //TODO check other corner cases, bad numerical ?
}


}

#endif
