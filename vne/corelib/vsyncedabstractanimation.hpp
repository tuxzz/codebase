#pragma once

#include <QObject>
#include <QAbstractAnimation>
#include "shiftedelapsedtimer.hpp"
#include "signalhub.hpp"

class VSyncedAnimationGroup;

class VSyncedAbstractAnimation : public QObject
{
    Q_OBJECT
    Q_PROPERTY(int currentLoop READ currentLoop NOTIFY currentLoopChanged)
    Q_PROPERTY(int currentTime READ currentTime WRITE setCurrentTime)
    Q_PROPERTY(QAbstractAnimation::Direction direction READ direction WRITE setDirection NOTIFY directionChanged)
    Q_PROPERTY(int duration READ duration)
    Q_PROPERTY(int loopCount READ loopCount WRITE setLoopCount)
    Q_PROPERTY(QAbstractAnimation::State state READ state NOTIFY stateChanged)
    Q_PROPERTY(qreal ratio READ ratio WRITE setRatio NOTIFY ratioChanged)

public:
    explicit VSyncedAbstractAnimation(QObject *parent = nullptr);
    explicit VSyncedAbstractAnimation(RatioHub *ratioHub, QObject *parent = nullptr);
    virtual ~VSyncedAbstractAnimation();

    int currentLoop() const;
    int currentLoopTime() const;
    int currentTime() const;
    QAbstractAnimation::Direction direction() const;
    virtual int duration() const = 0;
    VSyncedAnimationGroup *group() const;
    int loopCount() const;
    void setDirection(QAbstractAnimation::Direction direction);
    void setLoopCount(int loopCount);
    QAbstractAnimation::State state() const;
    int totalDuration() const;

    void setRatio(qreal ratio);
    qreal ratio() const;
    RatioHub *ratioHub() const;

    static SignalHub *animationSignalHub();

public slots:
    Q_INVOKABLE void pause();
    Q_INVOKABLE void resume();
    Q_INVOKABLE void setCurrentTime(int msecs);
    Q_INVOKABLE void setPaused(bool paused);
    Q_INVOKABLE void start(QAbstractAnimation::DeletionPolicy policy = QAbstractAnimation::KeepWhenStopped);
    Q_INVOKABLE void stop();
    Q_INVOKABLE void refresh(); /* safe to be called from QQuickView::beforeSynchronizing directly because gui thread is blocked */

protected:
    virtual void updateCurrentTime(int currentTime) = 0;
    virtual void updateDirection(QAbstractAnimation::Direction direction);
    virtual void updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState);

signals:
    void currentLoopChanged(int currentLoop);
    void directionChanged(QAbstractAnimation::Direction newDirection);
    void finished();
    void stateChanged(QAbstractAnimation::State newState, QAbstractAnimation::State oldState);
    void ratioChanged(qreal newRatio);

private:
    friend class VSyncedAnimationGroup;

    ShiftedElapsedTimer m_timer;
    int m_currentTime, m_currentLoop;
    int m_loopCount;
    qreal m_ratio;
    VSyncedAnimationGroup *m_group;
    QAbstractAnimation::Direction m_direction;
    QAbstractAnimation::State m_state;
    QAbstractAnimation::DeletionPolicy m_policy;
};
