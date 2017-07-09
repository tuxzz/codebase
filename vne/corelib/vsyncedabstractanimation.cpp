#include "vsyncedabstractanimation.hpp"
#include "vsyncedanimationgroup.hpp"
#include <QDebug>

static SignalHub *g_animationSignalHub = nullptr;

VSyncedAbstractAnimation::VSyncedAbstractAnimation(QObject *parent) : VSyncedAbstractAnimation(nullptr, parent)
{}

VSyncedAbstractAnimation::VSyncedAbstractAnimation(RatioHub *ratioHub, QObject *parent) : QObject(parent), m_timer(ratioHub)
{
    Q_ASSERT(QElapsedTimer::clockType() != QElapsedTimer::SystemTime && QElapsedTimer::clockType() != QElapsedTimer::TickCounter);
    Q_ASSERT(QElapsedTimer::isMonotonic());
    m_currentTime = 0;
    m_currentLoop = 0;
    m_loopCount = 1;
    m_ratio = 1.0;
    m_group = nullptr;
    m_direction = QAbstractAnimation::Forward;
    m_state = QAbstractAnimation::Stopped;
    m_policy = QAbstractAnimation::KeepWhenStopped;

    QObject::connect(animationSignalHub(), &SignalHub::hubSignal, this, &VSyncedAbstractAnimation::refresh);
}

VSyncedAbstractAnimation::~VSyncedAbstractAnimation()
{
    //we can't call stop here. Otherwise we get pure virtual calls
    if (m_state != QAbstractAnimation::Stopped)
    {
        auto oldState = m_state;
        m_state = QAbstractAnimation::Stopped;
        emit stateChanged(QAbstractAnimation::Stopped, oldState);
    }
    if(m_group)
        m_group->removeAnimation(this);
}

int VSyncedAbstractAnimation::currentLoop() const
{ return m_currentLoop; }

int VSyncedAbstractAnimation::currentLoopTime() const
{
    int dur = duration();
    if(dur == -1)
        return m_currentTime;
    else
    {
        if(m_currentTime == 0)
            return 0;
        else if(m_currentTime % dur == 0)
            return dur;
        else
            return m_currentTime % dur;
    }
}

int VSyncedAbstractAnimation::currentTime() const
{ return m_currentTime; }

QAbstractAnimation::Direction VSyncedAbstractAnimation::direction() const
{ return m_direction; }

VSyncedAnimationGroup *VSyncedAbstractAnimation::group() const
{ return m_group; }

int VSyncedAbstractAnimation::loopCount() const
{ return m_loopCount; }

void VSyncedAbstractAnimation::setDirection(QAbstractAnimation::Direction v)
{
    if(m_direction != v)
    {
        m_direction = v;
        updateDirection(v);
        emit directionChanged(v);
    }
}

void VSyncedAbstractAnimation::setLoopCount(int v)
{ m_loopCount = v; }

QAbstractAnimation::State VSyncedAbstractAnimation::state() const
{ return m_state; }

int VSyncedAbstractAnimation::totalDuration() const
{
    int dur = duration();
    return dur == -1 || m_loopCount == -1 ? -1 : dur * m_loopCount;
}

void VSyncedAbstractAnimation::setRatio(qreal v)
{
    if(m_timer.ratio() != v)
    {
        m_timer.setRatio(v);
        emit ratioChanged(v);
    }
}

qreal VSyncedAbstractAnimation::ratio() const
{ return m_timer.ratio(); }

RatioHub *VSyncedAbstractAnimation::ratioHub() const
{ return m_timer.hub(); }

SignalHub *VSyncedAbstractAnimation::animationSignalHub()
{
    if(!g_animationSignalHub)
        g_animationSignalHub = new SignalHub();
    return g_animationSignalHub;
}

void VSyncedAbstractAnimation::pause()
{
    refresh();
    if(m_state == QAbstractAnimation::Running)
    {
        auto oldState = m_state;
        m_state = QAbstractAnimation::Paused;
        updateState(m_state, oldState);
        emit stateChanged(QAbstractAnimation::Paused, oldState);
    }
    else
        qWarning()<<"Animation is not running.";
}

void VSyncedAbstractAnimation::resume()
{
    if(m_state == QAbstractAnimation::Paused)
    {
        m_timer.start();
        auto oldState = m_state;
        m_state = QAbstractAnimation::Running;
        updateState(m_state, oldState);
        emit stateChanged(QAbstractAnimation::Running, oldState);
    }
    else
        qWarning()<<"Animation is not paused.";
}

void VSyncedAbstractAnimation::setCurrentTime(int msecs)
{
    int tDur = totalDuration();
    if(tDur != -1)
        msecs = qBound(0, msecs, tDur);
    else
        msecs = std::max(0, msecs);
    if(m_currentTime != msecs)
    {
        m_currentTime = msecs;
        m_timer.start();
        refresh();
    }
}

void VSyncedAbstractAnimation::setPaused(bool paused)
{
    if(paused)
        pause();
    else
        resume();
}

void VSyncedAbstractAnimation::start(QAbstractAnimation::DeletionPolicy policy)
{
    if(m_state != QAbstractAnimation::Running)
    {
        m_timer.start();
        if(m_direction == QAbstractAnimation::Forward)
            m_currentTime = 0;
        else
            m_currentTime = m_loopCount == -1 ? duration() : totalDuration();
        m_policy = policy;
        auto oldState = m_state;
        m_state = QAbstractAnimation::Running;
        updateState(m_state, oldState);
        emit stateChanged(QAbstractAnimation::Running, oldState);
    }
}

void VSyncedAbstractAnimation::stop()
{
    refresh();
    if(m_state != QAbstractAnimation::Stopped)
    {
        auto oldState = m_state;
        m_state = QAbstractAnimation::Stopped;
        updateState(m_state, oldState);
        emit stateChanged(QAbstractAnimation::Stopped, oldState);
        if(m_policy == QAbstractAnimation::DeleteWhenStopped)
            deleteLater();
    }
}

void VSyncedAbstractAnimation::refresh()
{
    if(m_state != QAbstractAnimation::Running)
        return;

    int dur = duration();
    int tDur = dur == -1 || m_loopCount == -1 ? -1 : dur * m_loopCount;
    auto oldState = m_state;
    bool isFinished = false;

    if(dur == 0)
        return;

    int oldLoop;
    /* update */
    int deltaTime = m_timer.restart();

    if(m_direction == QAbstractAnimation::Forward)
    {
        if(!m_group)
            m_currentTime += deltaTime;

        oldLoop = m_currentLoop;
        if(m_currentTime == 0)
            m_currentLoop = 0;
        else if(m_currentTime % dur == 0)
            m_currentLoop = m_currentTime / dur - 1;
        else
            m_currentLoop = m_currentTime / dur;

        if(tDur != -1 && m_currentTime >= tDur)
        {
            m_currentTime = tDur;
            m_state = QAbstractAnimation::Stopped;
            isFinished = true;
        }
    }
    else
    {
        int t = tDur == -1 ? dur : tDur;
        if(!m_group)
            m_currentTime -= deltaTime;

        oldLoop = m_currentLoop;
        if(m_currentTime == tDur)
            m_currentLoop = 0;
        else if(m_currentTime % dur == 0)
            m_currentLoop = (t - m_currentTime) / dur - 1;
        else
            m_currentLoop = (t - m_currentTime) / dur;

        if(m_currentTime <= 0)
        {
            m_currentTime = 0;
            m_state = QAbstractAnimation::Stopped;
            isFinished = true;
        }
    }
    /* notify */
    updateCurrentTime(m_currentTime);
    if(m_currentLoop != oldLoop)
        emit currentLoopChanged(m_currentLoop);
    if(isFinished)
    {
        updateState(m_state, oldState);
        emit stateChanged(QAbstractAnimation::Stopped, oldState);
        emit finished();
        if(m_policy == QAbstractAnimation::DeleteWhenStopped)
            deleteLater();
    }
}

void VSyncedAbstractAnimation::updateDirection(QAbstractAnimation::Direction)
{}

void VSyncedAbstractAnimation::updateState(QAbstractAnimation::State, QAbstractAnimation::State)
{}


