function aa = orientationDistance(_R_desired, _R_actual)
    thresh = 1e-6;   # TODO #magic-number

    # TODO checks on the size 3x3
    R = transpose(_R_actual) *  _R_desired;   #  this is 'actual_R_desired'

    x = R(3,2) - R(2,3);
    y = R(1,3) - R(3,1);
    z = R(2,1) - R(1,2);
    norm = sqrt(x*x + y*y + z*z);

    if norm < thresh
        aa.axis = [0.0; 0.0; 1.0];  # arbitrary choice of (0,0,1) axis
        aa.angle= 0.0;
    end

    theta = atan2( norm, trace(R)-1 );
    aa.axis = [x/norm, y/norm, z/norm];
    aa.angle= theta;
    # TODO check corner cases, theta close to 0/PI, bad numerical
end
