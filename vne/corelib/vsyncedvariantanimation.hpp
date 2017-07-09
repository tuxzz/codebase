#pragma once

#include "vsyncedabstractanimation.hpp"
#include <QVariantAnimation>
#include <functional>

class VSyncedVariantAnimation : public VSyncedAbstractAnimation
{
    Q_OBJECT
    Q_PROPERTY(QVariant currentValue READ currentValue NOTIFY valueChanged)
    Q_PROPERTY(int duration READ duration WRITE setDuration)
    Q_PROPERTY(QEasingCurve easingCurve READ easingCurve WRITE setEasingCurve)
    Q_PROPERTY(QVariant endValue READ endValue WRITE setEndValue)
    Q_PROPERTY(QVariant startValue READ startValue WRITE setStartValue)

public:
    typedef std::function<QVariant (const QVariant &, const QVariant &, qreal)> Interpolator;

    explicit VSyncedVariantAnimation(QObject *parent = nullptr);
    virtual ~VSyncedVariantAnimation();

    QVariant currentValue() const;
    QEasingCurve easingCurve() const;
    QVariant endValue() const;
    QVariant keyValueAt(qreal step) const;
    QVariantAnimation::KeyValues keyValues() const;
    void setDuration(int msecs);
    void setEasingCurve(const QEasingCurve &easing);
    void setEndValue(const QVariant &value);
    void setKeyValueAt(qreal step, const QVariant &value);
    void setKeyValues(const QVariantAnimation::KeyValues &keyValues);
    void setStartValue(const QVariant &value);
    QVariant startValue() const;

    virtual int	duration() const override;

signals:
    void valueChanged(const QVariant &value);

protected:
    virtual void updateCurrentValue(const QVariant &value);

    virtual void updateCurrentTime(int t) override;
    virtual void updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState) override;

private:
    void updateInterpolator();

    int m_duration;
    QVariant m_currentValue;
    QEasingCurve m_easingCurve;
    QVariantAnimation::KeyValues m_keyValues;
    Interpolator m_interpolator;
};
