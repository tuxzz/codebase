#pragma once

#include "vsyncedanimationgroup.hpp"

class VSyncedPauseAnimation;

class VSyncedSequentialAnimationGroup : public VSyncedAnimationGroup
{
    Q_OBJECT
public:
    VSyncedSequentialAnimationGroup(QObject *parent = nullptr);
    virtual ~VSyncedSequentialAnimationGroup();

    VSyncedPauseAnimation *addPause(int msecs);
    VSyncedAbstractAnimation *currentAnimation() const;
    VSyncedPauseAnimation *insertPause(int index, int msecs);

    virtual int duration() const override;

signals:
    void currentAnimationChanged(VSyncedAbstractAnimation *current);

protected:
    virtual void updateCurrentTime(int currentTime) override;
    virtual void updateDirection(QAbstractAnimation::Direction direction) override;
    virtual void updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState) override;

private:
    void updateCurrentAnimation();

    mutable int m_accTime, m_iCurrent;
    mutable VSyncedAbstractAnimation *m_current;
};
