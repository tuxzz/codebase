#pragma once

#include <QElapsedTimer>
#include <QObject>
#include <QMetaObject>
#include "ratiohub.hpp"

class ShiftedElapsedTimer final
{
public:
    ShiftedElapsedTimer(RatioHub *hub = nullptr);
    ~ShiftedElapsedTimer();

    qint64 elapsed() const;
    qint64 nsecsElapsed() const;
    qint64 restart();
    void start();

    void setRatio(double v);
    double ratio() const;

    RatioHub *hub() const;

private slots:
    void removeHub();

private:
    mutable QElapsedTimer m_timer;
    mutable double m_time;
    double m_ratio;
    RatioHub *m_hub;
    QMetaObject::Connection m_conn0, m_conn1;
};
