#pragma once

#include "vsyncedabstractanimation.hpp"

class VSyncedPauseAnimation : public VSyncedAbstractAnimation
{
    Q_OBJECT

public:
    VSyncedPauseAnimation(QObject *parent = nullptr);
    VSyncedPauseAnimation(int msecs, QObject *parent = nullptr);
    virtual ~VSyncedPauseAnimation();

    void setDuration(int msecs);
    virtual int duration() const override;

protected:
    virtual void updateCurrentTime(int currentTime) override;

private:
    int m_duration;
};
