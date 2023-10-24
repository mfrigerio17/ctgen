#pragma once

#include <ctgen/cppiitrbd/dataset.h>
#include <ctgen/cppiitrbd/odistance.h>


namespace ctgen
{

template<class Traits, class Dataset>
void docompare(Dataset& data)
{
    Mx44 given, computed;
    ctgen::AxisAngle Rdiff;
    double err_pos = 0;
    double err_ori = 0;
    int count = 0;

    while( ! data.eof() )
    {
        Traits::computeMatrix(data, computed);
        data.readPose(given);

        Rdiff = ctgen::orientationDistance(
            (computed.block<3,3>(0,0)),
            (given.block<3,3>(0,0)));
        err_ori += Rdiff.angle;
        err_pos += (computed.block<3,1>(0,3)-given.block<3,1>(0,3)).norm();
        count++;
        //std::cout << err_ori << std::endl;
        //std::cout << given << std::endl << std::endl;
        //std::cout << computed << std::endl << std::endl;
    }

    err_pos /= count;
    err_ori /= count;

    std::cout << "Average position error   : " << err_pos << std::endl;
    std::cout << "Average orientation error: " << err_ori << std::endl;
    std::cout << "(number of comparisons: " << count << ")" << std::endl;
}

template<class Traits>
int testmain(int argc, char** argv)
{
    if(argc < 2) {
        std::cerr << "Please provide a dataset file." << std::endl;
        return -1;
    }

    std::string filename{argv[1]};
    std::string extension{ filename.substr(filename.find_last_of(".") + 1) };
    if(extension=="bin") {
        ctgen::NaiveBinDataset data(filename);
        docompare<Traits, ctgen::NaiveBinDataset>(data);
    } else if(extension=="csv") {
        ctgen::TextDataset data(filename);
        docompare<Traits, ctgen::TextDataset>(data);
    } else {
        std::cerr << "Unrecognized file extension " << extension << std::endl;
        return -1;
    }
    return 0;
}

}
