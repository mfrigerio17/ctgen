#include <ctgen/cppiitrbd/dataset.h>


void ctgen::TextDataset::readPose(Mx44& pose)
{
    readLine();
    pose.setIdentity();
    auto R = pose.block<3,3>(0,0);
    auto p = pose.block<3,1>(0,3);
    reader >> p(0) >> p(1) >> p(2);
    reader >> R(0,0) >> R(0,1) >> R(0,2)
           >> R(1,0) >> R(1,1) >> R(1,2)
           >> R(2,0) >> R(2,1) >> R(2,2);
}

void ctgen::TextDataset::readLine()
{
    std::string line;
    std::getline(source, line);
    reader.str(line);
    reader.seekg(std::ios_base::beg);
}


void ctgen::NaiveBinDataset::readPose(Mx44& pose)
{
    readBuff(12);
    pose.setIdentity();
    auto R = pose.block<3,3>(0,0);
    auto p = pose.block<3,1>(0,3);
    p(0) = buf[0];
    p(1) = buf[1];
    p(2) = buf[2];

    // expect the rotation matrix elements in row-major order, in the buffer
    for(int r=0;r<3;r++) {
        for(int c=0;c<3;c++) {
            R(r,c) = buf[3 + r*3 + c];
        }
    }
}
