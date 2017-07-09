#include "gamecontext.hpp"
#include "commandbase.hpp"
#include "corelib/ratiohub.hpp"
#include <QVariant>

GameContext::GameContext(QObject *parent) : QObject(parent)
{
    m_commandTimerRatioHub = new RatioHub();
    m_pc = 0;
    m_running = false;
    m_nextStep = false;
}

GameContext::~GameContext()
{
    for(CommandBase *cmd:m_commandList)
    {
        requestStop();
        delete cmd;
    }
    delete m_commandTimerRatioHub;
}

QVariant GameContext::globalVariable(const QString &name) const
{ return m_globalVariableDict.value(name); }

bool GameContext::hasGlobalVariable(const QString &name) const
{ return m_globalVariableDict.contains(name); }

bool GameContext::removeGlobalVariable(const QString &name)
{ return static_cast<bool>(m_globalVariableDict.remove(name)); }

void GameContext::trySetGlobalVariable(const QString &name, const QVariant &val)
{
    if(!hasGlobalVariable(name))
        setGlobalVariable(name, val);
}

void GameContext::setGlobalVariable(const QString &name, const QVariant &val)
{ m_localVariableDict.insert(name, val); }

QVariant GameContext::localVariable(const QString &name) const
{ return m_localVariableDict.value(name); }

bool GameContext::hasLocalVariable(const QString &name) const
{ return m_localVariableDict.contains(name); }

bool GameContext::removeLocalVariable(const QString &name)
{ return static_cast<bool>(m_localVariableDict.remove(name)); }

void GameContext::trySetLocalVariable(const QString &name, const QVariant &val)
{
    if(!hasLocalVariable(name))
        setLocalVariable(name, val);
}

void GameContext::setLocalVariable(const QString &name, const QVariant &val)
{ m_localVariableDict.insert(name, val); }

void GameContext::clearLocalVariable()
{ m_localVariableDict.clear(); }

RatioHub *GameContext::commandTimerRatioHub() const
{ return m_commandTimerRatioHub; }

void GameContext::setView(const QString &name, QObject *object)
{ m_viewDict.insert(name, object); }

QObject *GameContext::view(const QString &name) const
{ return m_viewDict.value(name, nullptr); }

void GameContext::setCommandList(const GameContext::CommandList &l)
{
    auto b = l.begin();
    auto e = l.end();
    for(auto it = b; it < e; ++it)
    {
        auto cmd = *it;
        cmd->setContext(this);
        cmd->setPosition(it - b);
    }
    m_commandList = l;
}

GameContext::CommandList GameContext::commandList() const
{ return m_commandList; }

int GameContext::pc() const
{ return m_pc; }

void GameContext::setPC(int v)
{
    Q_ASSERT(v >= 0);
    m_pc = v;
}

void GameContext::exec()
{
    if(!m_running)
    {
        m_nextStep = true;
        m_running = true;
        emit runningStateChanged(true);

        CommandBase *cmd = nullptr;
        while(m_nextStep && m_pc < m_commandList.size() && (cmd == nullptr || cmd->type() != CommandBase::AsyncWaiting))
        {
            cmd = m_commandList.at(m_pc);
            if(cmd->type() != CommandBase::Sync)
                m_unfinishedCommandList.append(cmd);
            ++m_pc;
            m_nextStep = cmd->exec();
            if(m_running && m_unfinishedCommandList.isEmpty())
            {
                m_running = false;
                emit runningStateChanged(false);
            }
        }
    }
}

void GameContext::execSingleStep()
{
    if(!m_running)
    {
        m_nextStep = false;
        m_running = true;
        emit runningStateChanged(true);

        CommandBase *cmd = m_commandList.at(m_pc);
        if(cmd->type() != CommandBase::Sync)
            m_unfinishedCommandList.append(cmd);
        ++m_pc;
        cmd->exec();
        if(m_running && m_unfinishedCommandList.isEmpty())
        {
            m_running = false;
            emit runningStateChanged(false);
        }
    }
}

void GameContext::requestStop()
{
    if(m_running)
    {
        m_nextStep = false;
        for(auto cmd:m_unfinishedCommandList)
            cmd->requestStop();
    }
}

bool GameContext::isRunning() const
{ return m_running; }

void GameContext::onCommandFinished(int pc)
{
    for(auto it = m_unfinishedCommandList.begin(); it < m_unfinishedCommandList.end(); ++it)
    {
        CommandBase *cmd = *it;
        if(cmd->position() == pc)
        {
            m_unfinishedCommandList.erase(it);
            break;
        }
    }
    auto cmd = m_commandList.at(pc);
    Q_ASSERT(cmd->type() != CommandBase::Sync);
    if(cmd->type() == CommandBase::AsyncWaiting)
    {
        CommandBase *cmd = nullptr;
        while(m_nextStep && m_pc < m_commandList.size() && (cmd == nullptr || cmd->type() != CommandBase::AsyncWaiting))
        {
            cmd = m_commandList.at(m_pc);
            if(cmd->type() != CommandBase::Sync)
                m_unfinishedCommandList.append(cmd);
            ++m_pc;
            m_nextStep = cmd->exec();
        }
    }
    if(m_running && m_unfinishedCommandList.isEmpty())
    {
        m_running = false;
        emit runningStateChanged(false);
    }
}
