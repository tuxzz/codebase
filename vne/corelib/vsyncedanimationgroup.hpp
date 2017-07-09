#pragma once

#include "vsyncedabstractanimation.hpp"
#include <QVector>

class VSyncedAnimationGroup : public VSyncedAbstractAnimation
{
    Q_OBJECT

public:
    VSyncedAnimationGroup(QObject *parent = nullptr);
    virtual ~VSyncedAnimationGroup();

    void addAnimation(VSyncedAbstractAnimation *animation);
    VSyncedAbstractAnimation *animationAt(int index) const;
    int	animationCount() const;
    void clear();
    int	indexOfAnimation(VSyncedAbstractAnimation *animation) const;
    void insertAnimation(int index, VSyncedAbstractAnimation *animation);
    void removeAnimation(VSyncedAbstractAnimation *animation);
    VSyncedAbstractAnimation *takeAnimation(int index);

private:
    QVector<VSyncedAbstractAnimation*> m_animationList;
};
