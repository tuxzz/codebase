#define _USE_MATH_DEFINES
#include <cmath>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QVector>
#include <al.h>
#include <alc.h>
#include <cassert>
#include <QDebug>
#include <QTimer>

static ALfloat listenerOrientation[] = {-1.0f, 1.0f, 0.0f, 1.0f, 1.0f, 0.0f};
static double phase = 0.0;
static QVector<ALshort> temp;

#define CHECK_ERROR() \
  {\
    ALenum error = alGetError(); \
    if(error != AL_NO_ERROR) \
      qFatal("ALERROR %d", error);\
  }

void fillBuffer(ALuint buffer, int bufferSize, int samprate = 48000)
{
  temp.resize(bufferSize);
  temp.fill(0);
  auto data = temp.data();
  for(int i = 0; i < bufferSize; ++i)
  {
    double t = static_cast<double>(i) / static_cast<double>(samprate);
    data[i] = static_cast<ALshort>(std::round(std::sin(phase + 2.0 * M_PI * 440.0 * t) * 16384.0));
  }
  phase = std::fmod(phase + 2.0 * M_PI * 440.0 * static_cast<double>(bufferSize) / static_cast<double>(samprate), 2 * M_PI);
  alBufferData(buffer, AL_FORMAT_MONO16, data, bufferSize * sizeof(ALshort), samprate);
  CHECK_ERROR();
}

static void list_audio_devices(const ALCchar *devices)
{
    const ALCchar *device = devices, *next = devices + 1;
    size_t len = 0;

    qDebug("Devices list:\n");
    qDebug("----------\n");
    while (device && *device != '\0' && next && *next != '\0')
    {
        qDebug("%s\n", device);
        len = strlen(device);
        device += (len + 1);
        next += (len + 2);
    }
    qDebug("----------\n");
}

int main(int argc, char *argv[])
{
  QGuiApplication app(argc, argv);

  QQmlApplicationEngine engine;
  engine.load(QUrl(QStringLiteral("qrc:/main.qml")));
  if (engine.rootObjects().isEmpty())
    return -1;

  /* initialize */
  {
      int result = alcIsExtensionPresent(NULL, "ALC_ENUMERATION_EXT");
      if(result == AL_FALSE)
        qDebug("No ALC_ENUMERATION_EXT support.");
      else
        list_audio_devices(alcGetString(NULL, ALC_DEVICE_SPECIFIER));
  }
  {
    int result = alIsExtensionPresent("AL_EXT_float32");
    if(result == AL_FALSE)
      qDebug("No AL_EXT_float32 support.");
  }

  ALCdevice *device = alcOpenDevice(nullptr);
  assert(device);
  ALCcontext *context = alcCreateContext(device, nullptr);
  assert(context);
  if(!alcMakeContextCurrent(context))
    qFatal("alcMakeContextCurrent(context) failed");

  alListener3f(AL_POSITION, 0.0f, 0.0f, 0.0f);
  CHECK_ERROR();
  alListener3f(AL_VELOCITY, 0.0f, 0.0f, 0.0f);
  CHECK_ERROR();
  alListenerfv(AL_ORIENTATION, listenerOrientation);
  CHECK_ERROR();

  ALuint source = -1;
  alGenSources(1, &source);
  CHECK_ERROR();
  alSourcef(source, AL_PITCH, 1.0);
  CHECK_ERROR();
  alSourcef(source, AL_GAIN, 1.0);
  CHECK_ERROR();
  alSource3f(source, AL_POSITION, 0, 0, 0);
  CHECK_ERROR();
  alSource3f(source, AL_VELOCITY, 0, 0, 0);
  CHECK_ERROR();
  alSourcei(source, AL_LOOPING, AL_FALSE);
  CHECK_ERROR();

  int bufferSize = 4096;
  /* allocate */
  ALuint bufferList[3];
  alGenBuffers(3, bufferList);
  CHECK_ERROR();
  fillBuffer(bufferList[0], bufferSize);
  fillBuffer(bufferList[1], bufferSize);
  fillBuffer(bufferList[2], bufferSize);
  //fillBuffer(bufferList[3], bufferSize);

  alSourceQueueBuffers(source, 3, bufferList);
  CHECK_ERROR();

  bool firstPlay = true;
  ALenum status = AL_PLAYING;

  QTimer t;
  t.setTimerType(Qt::PreciseTimer);


  QObject::connect(&t, &QTimer::timeout, [&](){
    if(firstPlay)
    {
      alSourcePlay(source);
      CHECK_ERROR();
      firstPlay = false;
    }
    if(status == AL_PLAYING)
    {
      // Check how much data is processed in OpenAL's internal queue
      ALint processed = 0;
      alGetSourcei(source, AL_BUFFERS_PROCESSED, &processed);
      CHECK_ERROR();

      //qDebug()<<"S:"<<source<<"P:"<<processed<<"A:"<<static_cast<int>(state == AL_PLAYING)<<"B1/2:"<<bufferList[0]<<bufferList[1];
      // add more buffers while we need them
      if(processed > 0)
      {
        for(int i = 0; i < processed; ++i)
        {
            ALuint bufferId = 0;
            alSourceUnqueueBuffers(source, 1, &bufferId);
            CHECK_ERROR();
            fillBuffer(bufferId, bufferSize);
            alSourceQueueBuffers(source, 1, &bufferId);
            CHECK_ERROR();
        }
      }
      alGetSourcei(source, AL_SOURCE_STATE, &status);
    }
  });

  t.start(1);

  return app.exec();
}
