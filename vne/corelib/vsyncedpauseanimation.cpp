#include "vsyncedpauseanimation.hpp"

VSyncedPauseAnimation::VSyncedPauseAnimation(QObject *parent) : VSyncedAbstractAnimation(parent)
{ m_duration = 250; }

VSyncedPauseAnimation::VSyncedPauseAnimation(int msecs, QObject *parent) : VSyncedAbstractAnimation(parent)
{
    Q_ASSERT(msecs >= 0);
    m_duration = msecs;
}

VSyncedPauseAnimation::~VSyncedPauseAnimation()
{}

void VSyncedPauseAnimation::setDuration(int msecs)
{
    Q_ASSERT(msecs >= 0);
    m_duration = msecs;
}

int VSyncedPauseAnimation::duration() const
{ return m_duration; }

void VSyncedPauseAnimation::updateCurrentTime(int)
{}
