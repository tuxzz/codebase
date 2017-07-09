#include "shiftedelapsedtimer.hpp"

ShiftedElapsedTimer::ShiftedElapsedTimer(RatioHub *hub)
{
    if(!QElapsedTimer::isMonotonic())
        qFatal("Timer is not monotonic.");
    if(QElapsedTimer::clockType() == QElapsedTimer::TickCounter)
        qFatal("Timer maybe overflow.");
    m_time = 0.0;
    m_ratio = 1.0;
    m_timer.start();
    if(hub)
    {
        m_conn0 = QObject::connect(hub, &RatioHub::ratioChanged, [this](double v){
            this->setRatio(v);
        });
        m_conn1 = QObject::connect(hub, &QObject::destroyed, [this](){
            this->removeHub();
        });
    }
}

ShiftedElapsedTimer::~ShiftedElapsedTimer()
{
    QObject::disconnect(m_conn1);
    QObject::disconnect(m_conn0);
}

qint64 ShiftedElapsedTimer::elapsed() const
{
    return static_cast<qint64>(m_time * 1e-6 + static_cast<double>(m_timer.elapsed()) * m_ratio + 0.5);
}

qint64 ShiftedElapsedTimer::nsecsElapsed() const
{
    return static_cast<qint64>(m_time + static_cast<double>(m_timer.nsecsElapsed()) * m_ratio + 0.5);
}

qint64 ShiftedElapsedTimer::restart()
{
    qint64 v = static_cast<qint64>(m_time * 1e-6 + static_cast<double>(m_timer.restart()) * m_ratio + 0.5);
    m_time = 0.0;
    return v;
}

void ShiftedElapsedTimer::start()
{
    m_time = 0.0;
    m_timer.start();
}

void ShiftedElapsedTimer::setRatio(double v)
{
    if(m_ratio != v)
    {
        double oldRatio = m_ratio;
        m_ratio = v;

        qint64 t = m_timer.nsecsElapsed();
        m_timer.start();
        m_time += static_cast<double>(t) * oldRatio;
    }
}

double ShiftedElapsedTimer::ratio() const
{ return m_ratio; }

RatioHub *ShiftedElapsedTimer::hub() const
{ return m_hub; }

void ShiftedElapsedTimer::removeHub()
{ m_hub = nullptr; }
