import QtQuick 2.8
import QtGraphicalEffects 1.0

Item {
    id: titleScreen;
    opacity: 0.0;

    Image {
        anchors.fill: parent
        source: "qrc:/title.jpg"
        asynchronous: false;
        cache: true;
        horizontalAlignment: Image.AlignHCenter;
        verticalAlignment: Image.AlignVCenter;
        mipmap: true;
        smooth: true;
    }

    Column {
        id: menuColumn;
        x: 48;
        anchors.bottom: parent.bottom;
        anchors.bottomMargin: 64;

        spacing: 24;

        TitleButton {
            id: startButton;
            text: "Start"
            width: 128;
            height: 36;

            onClicked: {
                console.log("clicked");
            }

            states: [
                State {
                    name: "hidden"; when: optionsButton.checked;
                    PropertyChanges { target: startButton; opacity: 0.0; enabled: false; }
                }
            ]

            transitions: Transition {
                NumberAnimation { property: "opacity"; easing.type: Easing.InOutQuad; duration: 250; }
            }
        }

        TitleButton {
            id: optionsButton
            text: "Options"
            width: 128;
            height: 36;
            checkable: true;

            onClicked: {
                console.log("clicked");
            }
        }

        TitleButton {
            id: exitButton;
            text: "Exit"
            width: 128;
            height: 36;

            onClicked: {
                console.log("clicked");
            }

            states: [
                State {
                    name: "hidden"; when: optionsButton.checked;
                    PropertyChanges { target: exitButton; opacity: 0.0; enabled: false; }
                }
            ]

            transitions: Transition {
                NumberAnimation { property: "opacity"; easing.type: Easing.InOutQuad; duration: 250; }
            }
        }
    }

    Item {
        id: titleTextGroup;
        opacity: 0.0;

        x: 48;
        anchors.bottom: menuColumn.top;
        anchors.bottomMargin: 36;

        width: titleText.width;
        height: titleText.height;

        Text {
            id: titleText;

            font.pixelSize: 64;
            font.underline: true;

            color: "white";
            textFormat: Text.PlainText;

            text: "Prologue";
        }

        DropShadow {
            anchors.fill: titleText;
            source: titleText;

            cached: true;
            horizontalOffset: 0;
            verticalOffset: 0;
            color: "black";
            radius: 8;
        }
    }

    ParallelAnimation {
        running: true;
        NumberAnimation { target: titleScreen; property: "opacity"; from: 0.0; to: 1.0; duration: 1000; easing.type: Easing.InOutQuart; }
        SequentialAnimation
        {
            PauseAnimation { duration: 250; }
            NumberAnimation { target: titleTextGroup; property: "opacity"; from: 0.0; to: 1.0; duration: 750; easing.type: Easing.InOutQuart; }
        }
    }
}
