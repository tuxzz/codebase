#include "spinrwlock.hpp"
#include <cassert>

SpinRWLock::SpinRWLock() : m_lock(0)
{
    assert(m_lock.is_lock_free());
}

SpinRWLock::~SpinRWLock()
{}

void SpinRWLock::lockRead()
{
    while(!tryLockRead())
        (void)0;
    return;
}

void SpinRWLock::lockWrite()
{
    while(!tryLockWrite())
        (void)0;
}

void SpinRWLock::release()
{
    int old = m_lock.exchange(-2);
    if(old >= 0)
        m_lock.store(old - 1);
    else if(old != -2)
    {
        assert(old != 0);
        m_lock.store(0);
    }
}

bool SpinRWLock::tryLockRead()
{
    int old = m_lock.exchange(-2);
    if(old >= 0)
    {
        m_lock.store(old + 1);
        return true;
    }
    else
    {
        m_lock.store(old);
        return false;
    }
}

bool SpinRWLock::tryLockWrite()
{
    int tmp = 0;
    return m_lock.compare_exchange_weak(tmp, -1);
}

int SpinRWLock::lockStatus() const
{
    int s;
    while(s = m_lock.load() != -2)
        (void)0;
    return s;
}
