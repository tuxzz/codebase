#include "commandbase.hpp"
#include <QtGlobal>
#include "gamecontext.hpp"

CommandBase::CommandBase(CommandType t)
{
    m_type = t;
    m_context = nullptr;
    m_position = -1;
}

CommandBase::~CommandBase()
{}

void CommandBase::requestStop()
{
    Q_ASSERT(m_type != Sync);
}

void CommandBase::load()
{}

void CommandBase::unload()
{}

CommandBase::CommandType CommandBase::type() const
{ return m_type; }

GameContext *CommandBase::context() const
{ return m_context; }

void CommandBase::setContext(GameContext *context)
{ m_context = context; }

int CommandBase::position() const
{ return m_position; }

void CommandBase::setPosition(int v)
{ m_position = v; }

PauseCommand::PauseCommand() : CommandBase(CommandBase::Sync)
{}

PauseCommand::~PauseCommand()
{}

bool PauseCommand::exec()
{
    return false;
}
