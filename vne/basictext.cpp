#include "basictext.hpp"
#include "corelib/vsyncedabstractanimation.hpp"
#include "gamecontext.hpp"
#include <QMetaObject>
#include <QDebug>

BasicText::BasicText(QObject *view, const QString &text, int wordMsecs, RatioHub *hub, bool styled, bool pause) : CommandBase(CommandBase::AsyncWaiting), m_timer(hub)
{
    Q_ASSERT(view && wordMsecs >= 0);
    m_view = view;
    const QMetaObject *metaObject = m_view->metaObject();
    m_property = metaObject->property(metaObject->indexOfProperty("text"));

    m_text = text;
    m_wordMsecs = wordMsecs;
    m_running = false;
    m_styled = styled;
    m_pause = pause;

    m_iWord = -1;
    m_iPosition = -1;

    if(styled)
    {
        // early verifying
        int n = text.size();
        for(int i = 0; i < n; i = BasicText::nextStyledWord(text, i))
            (void)0;
    }
}

BasicText::~BasicText()
{
    requestStop();
}

QObject *BasicText::view() const
{ return m_view; }

QString BasicText::text() const
{ return m_text; }

int BasicText::msecs() const
{ return m_wordMsecs; }

bool BasicText::exec()
{
    m_running = true;
    if(m_wordMsecs > 0)
    {
        m_iWord = 0;
        m_iPosition = 0;
        m_timer.start();
        conn = QObject::connect(VSyncedAbstractAnimation::animationSignalHub(), &SignalHub::hubSignal, [this](){
            this->refresh();
        });
    }
    else
    {
        m_property.write(m_view, m_text);
        requestStop();
    }
    return m_pause;
}

void BasicText::requestStop()
{
    if(m_running)
    {
        QObject::disconnect(conn);
        GameContext *ctx = context();
        ctx->onCommandFinished(position());
        m_running = false;
    }
}

int BasicText::nextStyledWord(const QString &s, int i)
{
    int n = s.size();
    ++i;
    while(i < n && (s[i] == '<' || s[i] == '&'))
    {
        if(s[i] == '<')
        {
            ++i;
            while(i < n && s[i] != '>')
                ++i;
            if(i >= n)
                qFatal("Broken styled text: '%s'", s.toUtf8().constData());
            ++i;
        }
        else if(s[i] == '&')
        {
            ++i;
            while(i < n && s[i] != ';')
                ++i;
            if(i >= n)
                qFatal("Broken styled text: '%s'", s.toUtf8().constData());
        }
    }
    return std::min(i, n);
}

void BasicText::refresh()
{
    qint64 t = m_timer.elapsed();
    int iCurrWord = t / m_wordMsecs;
    int n = m_text.size();
    if(m_iPosition <= n)
    {
        if(m_iWord != iCurrWord)
        {
            if(m_styled)
            {
                int deltaWord = iCurrWord - m_iWord;
                for(int i = 0; i < deltaWord && m_iPosition < n; ++i)
                    m_iPosition = BasicText::nextStyledWord(m_text, m_iPosition);
                m_property.write(m_view, m_text.left(m_iPosition));
            }
            else
            {
                m_property.write(m_view, m_text.left(iCurrWord));
                m_iPosition = iCurrWord;
            }
            m_iWord = iCurrWord;
        }
    }
    if(m_iPosition >= n)
        requestStop();
}
