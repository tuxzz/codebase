#pragma once

#include "commandbase.hpp"
#include "corelib/vsyncedvariantanimation.hpp"
#include <QObject>
#include <QMetaProperty>
#include "corelib/shiftedelapsedtimer.hpp"

class BasicText final : public CommandBase
{
public:
    BasicText(QObject *view, const QString &text, int wordMsecs, RatioHub *hub, bool styled, bool pause);
    ~BasicText();

    QObject *view() const;
    QString text() const;
    int msecs() const;

    bool exec() override;
    void requestStop() override;

    static int nextStyledWord(const QString &s, int i);

private:
    void refresh();

    QObject *m_view;
    QMetaProperty m_property;
    QString m_text;
    int m_wordMsecs;
    ShiftedElapsedTimer m_timer;

    QMetaObject::Connection conn;
    bool m_running, m_styled, m_pause;

    int m_iWord, m_iPosition;
};
