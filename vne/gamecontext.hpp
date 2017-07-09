#pragma once

#include <QObject>
#include <QHash>
#include <QVector>

class CommandBase;
class PauseCommand;
class RatioHub;

class GameContext final : public QObject
{
    Q_OBJECT

public:
    typedef QVector<CommandBase*> CommandList;

    explicit GameContext(QObject *parent = nullptr);
    ~GameContext();

    QVariant globalVariable(const QString &name) const;
    bool hasGlobalVariable(const QString &name) const;
    bool removeGlobalVariable(const QString &name);
    void trySetGlobalVariable(const QString &name, const QVariant &val);
    void setGlobalVariable(const QString &name, const QVariant &val);

    QVariant localVariable(const QString &name) const;
    bool hasLocalVariable(const QString &name) const;
    bool removeLocalVariable(const QString &name);
    void trySetLocalVariable(const QString &name, const QVariant &val);
    void setLocalVariable(const QString &name, const QVariant &val);
    void clearLocalVariable();

    RatioHub *commandTimerRatioHub() const;

    void setView(const QString &name, QObject *object);
    QObject *view(const QString &name) const;

    void setCommandList(const CommandList &l);
    CommandList commandList() const;

    int pc() const;
    void setPC(int v);

    Q_INVOKABLE void exec();
    Q_INVOKABLE void execSingleStep();
    Q_INVOKABLE void requestStop();

    bool isRunning() const;

public slots:
    void onCommandFinished(int pc);

signals:
    void runningStateChanged(bool running);

private:
    QHash<QString, QVariant> m_globalVariableDict, m_localVariableDict;
    QHash<QString, QObject*> m_viewDict;
    CommandList m_commandList;
    CommandList m_unfinishedCommandList;

    RatioHub *m_commandTimerRatioHub;

    int m_pc;
    bool m_running, m_nextStep;
};
