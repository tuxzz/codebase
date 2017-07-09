#pragma once

#include <QObject>

class RatioHub : public QObject
{
    Q_OBJECT

public:
    RatioHub(QObject *parent = nullptr);
    ~RatioHub();

    void setRatio(double v);
    double ratio() const;

signals:
    void ratioChanged(double);

private:
    double m_ratio;
};
