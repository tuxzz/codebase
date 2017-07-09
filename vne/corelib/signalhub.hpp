#pragma once

#include <QObject>

class SignalHub final : public QObject
{
    Q_OBJECT
public:
    SignalHub(QObject *parent = nullptr);
    ~SignalHub();

signals:
    void hubSignal();

};
