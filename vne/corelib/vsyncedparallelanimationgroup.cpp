#include "vsyncedparallelanimationgroup.hpp"
#include <algorithm>
#include <QDebug>

VSyncedParallelAnimationGroup::VSyncedParallelAnimationGroup(QObject *parent) : VSyncedAnimationGroup(parent)
{}

VSyncedParallelAnimationGroup::~VSyncedParallelAnimationGroup()
{}

int VSyncedParallelAnimationGroup::duration() const
{
    int v = 0;
    int n = animationCount();
    for(int i = 0; i < n; ++i)
    {
        int dur = animationAt(i)->totalDuration();
        if(dur == -1)
            return -1;
        else if(dur > v)
            v = dur;
    }
    return v;
}

void VSyncedParallelAnimationGroup::updateCurrentTime(int currentTime)
{
    Q_UNUSED(currentTime);
    int loopTime = currentLoopTime();
    int n = animationCount();
    if(direction() == QAbstractAnimation::Forward)
    {
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            if(animation->state() != QAbstractAnimation::Running)
                animation->start();
            animation->setCurrentTime(loopTime);
        }
    }
    else
    {
        int dur = duration();
        Q_ASSERT(dur != -1);
        int t = dur - currentLoopTime();
        for(int i = n - 1; i >= 0; --i)
        {
            auto animation = animationAt(i);
            if(animation->state() != QAbstractAnimation::Running)
                animation->start();
            animation->setCurrentTime(animation->totalDuration() - t);
        }
    }
}

void VSyncedParallelAnimationGroup::updateDirection(QAbstractAnimation::Direction direction)
{
    int n = animationCount();
    for(int i = 0; i < n; ++i)
    {
        auto animation = animationAt(i);
        animation->setDirection(direction);
    }
}

void VSyncedParallelAnimationGroup::updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState)
{
    int n = animationCount();
    if(newState == QAbstractAnimation::Running)
    {
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            if(oldState == QAbstractAnimation::Stopped)
                animation->start();
            else if(animation->state() == QAbstractAnimation::Paused)
                animation->resume();
        }
    }
    else if(newState == QAbstractAnimation::Paused)
    {
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            if(animation->state() == QAbstractAnimation::Running)
                animation->pause();
        }
    }
    else // QAbstractAnimation::Stopped
    {
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            animation->stop();
        }
    }
}
