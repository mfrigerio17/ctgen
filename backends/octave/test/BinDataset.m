classdef BinDataset < handle

properties
    f
endproperties

methods
function obj = BinDataset(filename)
    obj.f = fopen(filename, 'rb');
endfunction

function array = readVector(obj, count)
    [array, actual] = fread(obj.f, count, 'float32');
    if actual~=count
        warning('Unexpected amount of data read')
    end
endfunction

function [R,tr] = readPose(obj)
    [data, count] = fread(obj.f, 12, 'float32');
    if(count~=12)
        warning('Unexpected amount of data read')
    end
    tr = data(1:3);
    R  = zeros(3,3);
    # expect the rotation matrix elements in row-major order, in the buffer
    for r=1:3
        for c=1:3
            R(r,c) = data((r-1)*3 + c + 3);
        end
    end
endfunction

function ret = thereIsMore(obj)
    fread(obj.f, 1);
    if feof(obj.f)
        ret = false;
    else
        fseek(obj.f, -1, SEEK_CUR);
        ret = true;
    end
endfunction

function reset(obj)
    fseek(obj.f, 0, SEEK_SET);
end

function testMatrix(obj, mx, stateVarsCount, paramsCount)
    if feof(obj.f)
        warning('End of file. Perhaps you need to reset the dataset');
        return;
    end
    err_o = 0;
    err_p = 0;
    count = 0;
    updateMX = @obj._updateMatrix;
    if paramsCount > 0
        updateMX = @obj._updateMatrixWithParams;
    end
    while obj.thereIsMore()
        updateMX(mx, stateVarsCount, paramsCount);

        [R,tr] = obj.readPose();

        aa = orientationDistance(R, mx.mx(1:3,1:3));
        err_o = err_o + aa.angle;
        err_p = err_p + norm( tr-mx.mx(1:3,4) );
        count = count + 1;
    end
    display(['Average orientation error: ' num2str(err_o/count)]);
    display(['Average translation error: ' num2str(err_p/count)]);
endfunction

function _updateMatrix(obj, mx, stateVarsCount, _)
    q = obj.readVector(stateVarsCount);
    q = num2cell(q);
    mx.updateExplicit(q{:});
end

function _updateMatrixWithParams(obj, mx, stateVarsCount, paramsCount)
    q = obj.readVector(stateVarsCount);
    q = num2cell(q);
    p = obj.readVector(paramsCount);
    p = num2cell(p);
    mx.updateParams(p{:});
    mx.updateExplicit(q{:});
end

endmethods

endclassdef
