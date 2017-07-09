#include "vsyncedsequentialanimationgroup.hpp"
#include "vsyncedpauseanimation.hpp"
#include <QDebug>

VSyncedSequentialAnimationGroup::VSyncedSequentialAnimationGroup(QObject *parent) : VSyncedAnimationGroup(parent)
{
    m_iCurrent = 0;
    m_current = nullptr;
}

VSyncedSequentialAnimationGroup::~VSyncedSequentialAnimationGroup()
{}

VSyncedPauseAnimation *VSyncedSequentialAnimationGroup::addPause(int msecs)
{ return insertPause(animationCount(), msecs); }

VSyncedAbstractAnimation *VSyncedSequentialAnimationGroup::currentAnimation() const
{
    const_cast<VSyncedSequentialAnimationGroup*>(this)->updateCurrentAnimation();
    return m_current;
}

VSyncedPauseAnimation *VSyncedSequentialAnimationGroup::insertPause(int index, int msecs)
{
    auto animation = new VSyncedPauseAnimation(msecs);
    insertAnimation(index, animation);
    return animation;
}

int VSyncedSequentialAnimationGroup::duration() const
{
    int dur = 0;
    int n = animationCount();
    for(int i = 0; i < n; ++i)
    {
        auto animation = animationAt(i);
        int t = animation->totalDuration();
        if(t == -1)
            return -1;
        dur += t;
    }
    return dur;
}

void VSyncedSequentialAnimationGroup::updateCurrentTime(int)
{
    updateCurrentAnimation();

    int clt = currentLoopTime();
    int n = animationCount();
    if(m_current && m_current->state() != QAbstractAnimation::Running)
        m_current->start();
    if(direction() == QAbstractAnimation::Forward)
    {
        int acc = 0;
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            animation->setCurrentTime(clt - acc);
            acc += animation->totalDuration();
        }
    }
    else
    {
        int acc = duration();
        for(int i = n - 1; i >= 0; --i)
        {
            auto animation = animationAt(i);
            acc -= animation->totalDuration();
            animation->setCurrentTime(clt - acc);
        }
    }
}

void VSyncedSequentialAnimationGroup::updateDirection(QAbstractAnimation::Direction direction)
{
    int n = animationCount();
    for(int i = 0; i < n; ++i)
    {
        auto animation = animationAt(i);
        animation->setDirection(direction);
    }
    updateCurrentAnimation();
}

void VSyncedSequentialAnimationGroup::updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState)
{
    int n = animationCount();
    updateCurrentAnimation();
    if(newState = QAbstractAnimation::Running)
    {
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            if(i != m_iCurrent)
                animation->stop();
            else
            {
                if(oldState == QAbstractAnimation::Stopped)
                    animation->start();
                else if(animation->state() == QAbstractAnimation::Paused)
                    animation->resume();
            }
        }
    }
    else if(newState == QAbstractAnimation::Paused)
    {
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            if(i != m_iCurrent)
                animation->stop();
            else if(animation->state() == QAbstractAnimation::Running)
                animation->pause();
        }
    }
    else // QAbstractAnimation::Stopped
    {
        for(int i = 0; i < n; ++i)
            animationAt(i)->stop();
    }
}

void VSyncedSequentialAnimationGroup::updateCurrentAnimation()
{
    int n = animationCount();
    int clt = currentLoopTime();
    auto oldCurrent = m_current;
    m_current = nullptr;
    if(direction() == QAbstractAnimation::Forward)
    {
        int acc = 0;
        for(int i = 0; i < n; ++i)
        {
            auto animation = animationAt(i);
            int t = animation->totalDuration();
            if(t == -1 || (clt < acc + t && clt >= acc))
            {
                m_iCurrent = i;
                m_current = animation;
                break;
            }
            acc += t;
        }
    }
    else
    {
        int acc = duration();
        for(int i = n - 1; i >= 0; --i)
        {
            auto animation = animationAt(i);
            int t = animation->totalDuration();
            if(t == -1 || (clt < acc && clt >= acc - t))
            {
                m_iCurrent = i;
                m_current = animation;
                break;
            }
            acc -= t;
        }
    }
    if(m_current != oldCurrent)
        emit currentAnimationChanged(m_current);
}
