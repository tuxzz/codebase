#pragma once

#include <functional>

class GameContext;

class CommandBase
{
public:
    enum CommandType
    {
        Sync,
        AsyncNotWaiting,
        AsyncWaiting
    };

    CommandBase(CommandType type);
    virtual ~CommandBase();

    virtual bool exec() = 0;
    virtual void requestStop();
    virtual void load();
    virtual void unload();

    CommandType type() const;

    GameContext *context() const;
    void setContext(GameContext *context);

    int position() const;
    void setPosition(int v);

private:
    CommandType m_type;
    GameContext *m_context;

    int m_position;
};

class PauseCommand final : public CommandBase
{
public:
    PauseCommand();
    ~PauseCommand();

    bool exec() override;

};
