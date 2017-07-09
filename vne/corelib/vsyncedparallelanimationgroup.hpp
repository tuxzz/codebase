#pragma once

#include "vsyncedanimationgroup.hpp"

class VSyncedParallelAnimationGroup : public VSyncedAnimationGroup
{
    Q_OBJECT
public:
    VSyncedParallelAnimationGroup(QObject *parent = nullptr);
    virtual ~VSyncedParallelAnimationGroup();

    virtual int	duration() const override;

protected:
    virtual void updateCurrentTime(int currentTime) override;
    virtual void updateDirection(QAbstractAnimation::Direction direction) override;
    virtual void updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState) override;
};
