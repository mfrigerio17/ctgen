function d = orientationDistance(x_R_desired, x_R_actual)
    thresh = 1e-6;   % TODO %magic-number

    % TODO checks on the size 3x3
    R = x_R_actual(1:3,1:3)' * x_R_desired(1:3,1:3);   %  this is 'actual_R_desired'

    x = R(3,2) - R(2,3);
    y = R(1,3) - R(3,1);
    z = R(2,1) - R(1,2);
    vnorm = sqrt(x*x + y*y + z*z);  % =0 when R is symmetric
    if vnorm < thresh
        theta = atan2( 0, trace(R)-1 );
        % the angle can only be 0 or pi
        if abs(theta) > thresh
            %%assert( ismembertol(abs(theta), pi) ); % theta must be pi, in this case
            % the axis is any non-zero column of I+R
            aux = R + eye(3);
            i = find( sum(aux,2)~=0, 1 );
            d.axis = aux(:,i)/norm(aux(:,i));
            d.angle = pi;
            return
        else
            d.axis  = [0.0, 0.0, 1.0]; % arbitrary choice of (0,0,1) axis
            d.angle = 0;
            return
        end
    end

    theta = atan2( vnorm, trace(R)-1 );
    d.axis = [x, y, z]/vnorm;
    d.angle = theta;
