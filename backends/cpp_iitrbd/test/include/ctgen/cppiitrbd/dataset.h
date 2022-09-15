#ifndef CTGEN_CPP_IITRBD_BACKEND_TESTING_DATASET_H
#define CTGEN_CPP_IITRBD_BACKEND_TESTING_DATASET_H

#include <iostream>
#include <fstream>
#include <exception>

#include <iit/rbd/rbd.h>


namespace ctgen
{

using Mx44 = iit::rbd::PlainMatrix<double, 4, 4>;

/**
 * Trivial wrapper of a test dataset in text format.
 *
 * A test dataset contains the coefficients of an homogeneous transformation
 * matrix for different values of the variables.
 *
 * The expected format of the underlying data file is one entry on each
 * line, with space-separated values.
 * The dataset must contain a value for each variable the transforms depends
 * on, then 12 more coefficients: first the three elements of the position
 * vector, than the 9 elements of the rotation matrix, row wise.
 *
 */
class TextDataset
{
public:
    TextDataset(const std::string&  file) {
        source.open( file, std::ios::in);
        if( !source.is_open() ) {
            throw std::runtime_error("Could not open file " + file);
        }
    }

    ~TextDataset() {
        source.close();
    }

    bool eof() { return source.eof(); }

    /**
     * A pose must be stored as a 12 element vector, first the three elements of the
     * position vector, than the 9 elements of the rotation matrix, row wise.
     */
    void readPose(Mx44& pose);

    template<typename V>
    void readVector(unsigned int count, V& out)
    {
        readLine();
        for(unsigned int c=0; c<count; c++) {
            reader >> out(c);
        }
    }

private:
    void readLine();

    std::ifstream source;
    std::istringstream reader;
};

/**
 * A wrapper for a test dataset in binary format.
 * For the expected data format see `TextDataset`
 */
class NaiveBinDataset
{
public:
    NaiveBinDataset(const std::string&  file) {
        source.open( file, std::ios::in | std::ios::binary);
        if( !source.is_open() ) {
            throw std::runtime_error("Could not open file " + file);
        }
    }

    ~NaiveBinDataset() {
        source.close();
    }

    bool eof() { return source.eof(); }

    /**
     * A pose must be stored as a 12 element vector, first the three elements of the
     * position vector, than the 9 elements of the rotation matrix, row wise.
     */
    void readPose(Mx44& pose);

    template<typename V>
    void readVector(unsigned int count, V& out)
    {
        readBuff(count);
        for(unsigned int c=0; c<count; c++) {
            out(c) = buf[c];
        }
    }

private:
    void readBuff(unsigned short howmany) {
        source.read(reinterpret_cast<char*>(buf), howmany*sizeof(float));
        source.peek(); // make sure to trigger EOF now, if there are no more chars
    }

    float buf[64];
    std::ifstream source;
};

}



#endif

