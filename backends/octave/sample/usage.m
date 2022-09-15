CtgenSampleModelConstants_init;  % global variables with the model constants

ExG = frameE_xh_frameG();      % creates a transform object

varstate.q0 = rand(1,1);       % set the variables status
varstate.q1 = rand(1,1);
varstate.q2 = rand(1,1);

ExG.update( varstate );             % update the transform with the variables values
ExG.updateExplicit(0.1, 0.2, 0.3);  % one argument for each variable

v2 = ExG.mx * [rand(3,1); 1];  % the `mx` field is the actual matrix



DxB = frameD_xh_frameB();      % another transform; this one is parametric

DxB.updateParams( rand(1,1), rand(1,1) );   % set new parameters values
                                            % does NOT update the matrix

DxB.update([]);      % still needed to apply the new parameters
                     % by chance this transform does not depend on any variable
