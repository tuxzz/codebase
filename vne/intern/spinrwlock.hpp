#pragma once

#include <atomic>

class SpinRWLock final
{
public:
    SpinRWLock();
    ~SpinRWLock();

    void lockRead();
    void lockWrite();
    void release();

    bool tryLockRead();
    bool tryLockWrite();

    int lockStatus() const; /* 0 = unlocked, -1 wlocked, >=1 rlocked */

private:
    std::atomic_int m_lock;
};
