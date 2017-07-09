TEMPLATE = app

QT += qml quick
CONFIG += c++11

SOURCES += main.cpp \
    corelib/vsyncedabstractanimation.cpp \
    corelib/vsyncedvariantanimation.cpp \
    intern/spinrwlock.cpp \
    corelib/vsyncedanimationgroup.cpp \
    corelib/vsyncedparallelanimationgroup.cpp \
    corelib/vsyncedsequentialanimationgroup.cpp \
    corelib/vsyncedpauseanimation.cpp \
    gamecontext.cpp \
    commandbase.cpp \
    corelib/shiftedelapsedtimer.cpp \
    basictext.cpp \
    corelib/signalhub.cpp \
    corelib/ratiohub.cpp

RESOURCES += qml.qrc

# Additional import path used to resolve QML modules in Qt Creator's code model
QML_IMPORT_PATH =

# Additional import path used to resolve QML modules just for Qt Quick Designer
QML_DESIGNER_IMPORT_PATH =

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += targets

win32 {
    QMAKE_CXXFLAGS_RELEASE += /GL
    QMAKE_LFLAGS_RELEASE += /LTCG
}

HEADERS += \
    corelib/vsyncedabstractanimation.hpp \
    corelib/vsyncedvariantanimation.hpp \
    intern/find.hpp \
    intern/find_impl.hpp \
    intern/spinrwlock.hpp \
    corelib/vsyncedanimationgroup.hpp \
    corelib/vsyncedparallelanimationgroup.hpp \
    corelib/vsyncedsequentialanimationgroup.hpp \
    corelib/vsyncedpauseanimation.hpp \
    gamecontext.hpp \
    commandbase.hpp \
    corelib/shiftedelapsedtimer.hpp \
    basictext.hpp \
    corelib/signalhub.hpp \
    corelib/ratiohub.hpp
