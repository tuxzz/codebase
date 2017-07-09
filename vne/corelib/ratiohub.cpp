#include "ratiohub.hpp"

RatioHub::RatioHub(QObject *parent) : QObject(parent)
{
    m_ratio = 1.0;
}

RatioHub::~RatioHub()
{}

void RatioHub::setRatio(double v)
{
    if(m_ratio != v)
    {
        m_ratio = v;
        emit ratioChanged(v);
    }
}

double RatioHub::ratio() const
{ return m_ratio; }
