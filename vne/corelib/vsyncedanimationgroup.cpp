#include "vsyncedanimationgroup.hpp"

VSyncedAnimationGroup::VSyncedAnimationGroup(QObject *parent) : VSyncedAbstractAnimation(parent)
{}

VSyncedAnimationGroup::~VSyncedAnimationGroup()
{ clear(); }

void VSyncedAnimationGroup::addAnimation(VSyncedAbstractAnimation *animation)
{ insertAnimation(animationCount(), animation); }

VSyncedAbstractAnimation *VSyncedAnimationGroup::animationAt(int index) const
{ return m_animationList.at(index); }

int VSyncedAnimationGroup::animationCount() const
{ return m_animationList.size(); }

void VSyncedAnimationGroup::clear()
{
    QVector<VSyncedAbstractAnimation*> l(m_animationList);
    for(auto x:l)
        delete x;
}

int VSyncedAnimationGroup::indexOfAnimation(VSyncedAbstractAnimation *animation) const
{ return m_animationList.indexOf(animation); }

void VSyncedAnimationGroup::insertAnimation(int index, VSyncedAbstractAnimation *animation)
{
    Q_ASSERT(m_animationList.indexOf(animation) == -1);
    m_animationList.insert(index, animation);
    animation->setParent(this);
    animation->m_group = this;
}

void VSyncedAnimationGroup::removeAnimation(VSyncedAbstractAnimation *animation)
{
    Q_ASSERT(animation->m_group == this);
    animation->setParent(nullptr);
    animation->m_group = nullptr;
    m_animationList.removeOne(animation);
}

VSyncedAbstractAnimation *VSyncedAnimationGroup::takeAnimation(int index)
{
    auto animation = m_animationList.at(index);
    animation->setParent(nullptr);
    animation->m_group = nullptr;
    m_animationList.removeAt(index);
    return animation;
}
