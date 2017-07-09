#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickView>
#include <QSurfaceFormat>
#include <QQuickItem>
#include <QDebug>
#include <QQmlContext>
#include <QTimer>
#include <QFontDatabase>

#include "corelib/vsyncedabstractanimation.hpp"
#include "basictext.hpp"
#include "gamecontext.hpp"

int main(int argc, char *argv[])
{
    //SetEnvironmentVariableW(L"QSG_RENDER_LOOP", L"threaded");
    QGuiApplication app(argc, argv);
    QFontDatabase::addApplicationFont(":/DroidSansFallbackFull.ttf");
    app.setAttribute(Qt::AA_UseDesktopOpenGL);
    app.setAttribute(Qt::AA_CompressHighFrequencyEvents);
    QFont defaultFont("Droid Sans Fallback");
    app.setFont(defaultFont);

    auto fmt = QSurfaceFormat::defaultFormat();
    fmt.setRenderableType(QSurfaceFormat::OpenGL);
    fmt.setVersion(4, 5);
    fmt.setProfile(QSurfaceFormat::CoreProfile);

    fmt.setSwapBehavior(QSurfaceFormat::TripleBuffer);
    fmt.setSamples(16);
    fmt.setSwapInterval(1);

    fmt.setStereo(false);

    GameContext *ctx = new GameContext();

    QQuickView rootView;
    rootView.setMinimumSize(QSize(1280, 720));
    rootView.setMaximumSize(QSize(1280, 720));
    rootView.rootContext()->setContextProperty("game", ctx);
    rootView.setSurfaceType(QSurface::OpenGLSurface);
    rootView.setFormat(fmt);
    rootView.setSource(QUrl(QStringLiteral("qrc:/main.qml")));
    rootView.resize(1280, 720);
    rootView.show();

    /*QObject::connect(&rootView, &QQuickView::frameSwapped, [&](){
        VSyncedAbstractAnimation::animationSignalHub()->hubSignal();
        rootView.update();
    });*/
    QObject::connect(&rootView, &QQuickView::frameSwapped, VSyncedAbstractAnimation::animationSignalHub(), &SignalHub::hubSignal);
    QObject::connect(&rootView, &QQuickView::frameSwapped, &rootView, &QQuickView::update);

    QObject *textView = rootView.rootObject();
    Q_ASSERT(textView);

    GameContext::CommandList cmdList;
    cmdList.append(new BasicText(textView, "<b>Hello world!</b> This is a <font color=\"red\">styled</font> testing text.", 125, ctx->commandTimerRatioHub(), true, false));
    cmdList.append(new BasicText(textView, "You should use &amp;amp; for '&amp;', or &amp;lt; for '&lt;', or &amp;gt; for '&gt;'.", 125, ctx->commandTimerRatioHub(), true, false));
    cmdList.append(new BasicText(textView, "You can also mix them, like a strong italic <b><i>this =&gt; &lt;&amp;&gt;</i></b>.", 125, ctx->commandTimerRatioHub(), true, false));
    cmdList.append(new BasicText(textView, "Or maybe you just want to use plain text for many plain text.", 125, ctx->commandTimerRatioHub(), false, false));
    ctx->setCommandList(cmdList);
    ctx->commandTimerRatioHub()->setRatio(1024.0);

    int ret = app.exec();
    return ret;
}
