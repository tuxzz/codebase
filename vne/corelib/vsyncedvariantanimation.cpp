#include "vsyncedvariantanimation.hpp"
#include "intern/find.hpp"
#include <algorithm>
#include <QLine>
#include <QLineF>
#include <QRect>
#include <QRectF>
#include <QColor>
#include <QQuaternion>
#include <QVector2D>
#include <QVector3D>
#include <QVector4D>

template<typename T>static T iplFunc(const T &a, const T &b, qreal ratio)
{ return static_cast<T>(a + (b - a) * ratio); }

template<>static QLine iplFunc(const QLine &a, const QLine &b, qreal ratio)
{
    return QLine(iplFunc(a.p1(), b.p1(), ratio),
                 iplFunc(a.p2(), b.p2(), ratio));
}

template<>static QLineF iplFunc(const QLineF &a, const QLineF &b, qreal ratio)
{
    return QLineF(iplFunc(a.p1(), b.p1(), ratio),
                  iplFunc(a.p2(), b.p2(), ratio));
}

template<>static QRect iplFunc(const QRect &a, const QRect &b, qreal ratio)
{
    return QRect(iplFunc(a.topLeft(), b.topLeft(), ratio),
                 iplFunc(a.bottomRight(), b.bottomRight(), ratio));
}

template<>static QRectF iplFunc(const QRectF &a, const QRectF &b, qreal ratio)
{
    return QRectF(iplFunc(a.topLeft(), b.topLeft(), ratio),
                  iplFunc(a.bottomRight(), b.bottomRight(), ratio));
}

template<>static QColor iplFunc(const QColor &a,const QColor &b, qreal ratio)
{
    return QColor(qBound(0, iplFunc(a.red(), b.red(), ratio), 255),
                  qBound(0, iplFunc(a.green(), b.green(), ratio), 255),
                  qBound(0, iplFunc(a.blue(), b.blue(), ratio), 255),
                  qBound(0, iplFunc(a.alpha(), b.alpha(), ratio), 255));
}

template<>static QQuaternion iplFunc(const QQuaternion &a,const QQuaternion &b, qreal ratio)
{ return QQuaternion::slerp(a, b, ratio); }

template<typename T>static QVariant generalInterpolator(const QVariant &a, const QVariant &b, qreal ratio)
{ return QVariant(iplFunc(qvariant_cast<T>(a), qvariant_cast<T>(b), ratio)); }

static VSyncedVariantAnimation::Interpolator getInterpolator(int typeId)
{
    switch(typeId)
    {
        case QMetaType::Int:
            return generalInterpolator<int>;
        case QMetaType::UInt:
            return generalInterpolator<uint>;
        case QMetaType::Double:
            return generalInterpolator<double>;
        case QMetaType::Float:
            return generalInterpolator<float>;
        case QMetaType::QLine:
            return generalInterpolator<QLine>;
        case QMetaType::QLineF:
            return generalInterpolator<QLineF>;
        case QMetaType::QPoint:
            return generalInterpolator<QPoint>;
        case QMetaType::QPointF:
            return generalInterpolator<QPointF>;
        case QMetaType::QSize:
            return generalInterpolator<QSize>;
        case QMetaType::QSizeF:
            return generalInterpolator<QSizeF>;
        case QMetaType::QRect:
            return generalInterpolator<QRect>;
        case QMetaType::QRectF:
            return generalInterpolator<QRectF>;
        case QMetaType::QColor:
            return generalInterpolator<QColor>;
        case QMetaType::QQuaternion:
            return generalInterpolator<QQuaternion>;
        case QMetaType::QVector2D:
            return generalInterpolator<QVector2D>;
        case QMetaType::QVector3D:
            return generalInterpolator<QVector3D>;
        case QMetaType::QVector4D:
            return generalInterpolator<QVector4D>;
        default:
            qFatal("No interpolator available.");
    }
    return nullptr;
}

VSyncedVariantAnimation::VSyncedVariantAnimation(QObject *parent) : VSyncedAbstractAnimation(parent)
{
    m_duration = 250;
    m_keyValues.append(qMakePair(0.0, QVariant()));
    m_keyValues.append(qMakePair(1.0, QVariant()));
}

VSyncedVariantAnimation::~VSyncedVariantAnimation()
{}

QVariant VSyncedVariantAnimation::currentValue() const
{ return m_currentValue; }

QEasingCurve VSyncedVariantAnimation::easingCurve() const
{ return m_easingCurve; }

QVariant VSyncedVariantAnimation::endValue() const
{ return m_keyValues.last().second; }

QVariant VSyncedVariantAnimation::keyValueAt(qreal step) const
{
    Q_ASSERT(step >= 0.0 && step <= 1.0);
    auto it = find(m_keyValues.begin(), m_keyValues.end(), step, [](const auto &v){ return v.first; });
    if(it == m_keyValues.end())
        return QVariant();
    return it->second;
}

QVariantAnimation::KeyValues VSyncedVariantAnimation::keyValues() const
{ return m_keyValues; }

void VSyncedVariantAnimation::setDuration(int msecs)
{
    Q_ASSERT(msecs >= 0);
    m_duration = msecs;
}

void VSyncedVariantAnimation::setEasingCurve(const QEasingCurve &easing)
{ m_easingCurve = easing; }

void VSyncedVariantAnimation::setEndValue(const QVariant &value)
{
    m_keyValues.last().second = value;
    if(!m_keyValues.first().second.isValid())
        m_keyValues.first().second = value;
}

void VSyncedVariantAnimation::setKeyValueAt(qreal step, const QVariant &value)
{
    Q_ASSERT(value.isValid());
    auto it = findGEQ(m_keyValues.begin(), m_keyValues.end(), step, [](const auto &v){ return v.first; });
    if(it == m_keyValues.end() || it->first != step)
        m_keyValues.insert(it, qMakePair(step, value));
    else
        it->second = value;
}

void VSyncedVariantAnimation::setKeyValues(const QVariantAnimation::KeyValues &keyValues)
{
    m_keyValues = keyValues;
    std::sort(m_keyValues.begin(), m_keyValues.end(), [](const auto &a, const auto &b){ return a.first < b.first; });
    Q_ASSERT(keyValues.size() >= 2 && keyValues.first().first == 0.0 && keyValues.last().first == 1.0);
    for(auto it = m_keyValues.cbegin() + 1; it < m_keyValues.cend(); ++it)
    {
        Q_ASSERT(it->first > (it - 1)->first);
        Q_ASSERT(it->second.isValid());
        Q_ASSERT(it->second.userType() == (it - 1)->second.userType());
    }
}

void VSyncedVariantAnimation::setStartValue(const QVariant &value)
{
    m_keyValues.first().second = value;
    if(!m_keyValues.last().second.isValid())
        m_keyValues.last().second = value;
}

QVariant VSyncedVariantAnimation::startValue() const
{ return m_keyValues.first().second; }

int VSyncedVariantAnimation::duration() const
{ return m_duration; }

void VSyncedVariantAnimation::updateCurrentValue(const QVariant &)
{}

void VSyncedVariantAnimation::updateCurrentTime(int)
{
    Q_ASSERT(m_interpolator);
    qreal progress = static_cast<qreal>(currentLoopTime()) / static_cast<qreal>(m_duration);
    auto it = findLEQ(m_keyValues.cbegin(), m_keyValues.cend(), progress, [](const auto &p){ return p.first; });
    if(it == m_keyValues.cend())
        m_currentValue = m_keyValues.constFirst().second;
    else if(it == m_keyValues.cend() - 1)
        m_currentValue = m_keyValues.constLast().second;
    else
    {
        auto nit = it + 1;
        qreal a = it->first;
        qreal b = nit->first;
        qreal v = m_easingCurve.valueForProgress((progress - a) / (b - a));
        m_currentValue = m_interpolator(it->second, nit->second, v);
    }
    updateCurrentValue(m_currentValue);
    emit valueChanged(m_currentValue);
}

void VSyncedVariantAnimation::updateState(QAbstractAnimation::State newState, QAbstractAnimation::State oldState)
{
    VSyncedAbstractAnimation::updateState(newState, oldState);
    if(newState == QAbstractAnimation::Running)
        updateInterpolator();
}

void VSyncedVariantAnimation::updateInterpolator()
{ m_interpolator = getInterpolator(m_keyValues.first().second.userType()); }
