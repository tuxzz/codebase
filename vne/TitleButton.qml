import QtQuick 2.8
import QtGraphicalEffects 1.0
import QtQuick.Controls 2.2

AbstractButton {
    id: root
    property alias textSize: textBox.font.pixelSize;

    MouseArea {
        id: mouseArea
        anchors.fill: parent;

        hoverEnabled: true;
        onClicked: {
            if(root.checkable)
            {
                root.toggle();
                root.toggled();
            }
            root.clicked();
        }
        onPressed: root.pressed;
        onReleased: root.released;

        Rectangle
        {
            id: back;
            anchors.fill: parent;
            opacity: 0.0;
            radius: 1.0;

            gradient: Gradient {
                GradientStop {
                  position: 0.0;
                  color: "#00F0F0F0";
                }
                GradientStop {
                  position: 1.0;
                  color: "#FFF0F0F0";
                }
            }

            states: [
                State {
                    name: "mouseEntered"; when: mouseArea.containsMouse && !root.checked;
                    PropertyChanges { target: back; opacity: 1.0; }
                },
                State {
                    name: "mouseExited"; when: !mouseArea.containsMouse && !root.checked;
                    PropertyChanges { target: back; opacity: 0.5; }
                }
            ]

            transitions: Transition {
                NumberAnimation { property: "opacity"; easing.type: Easing.InOutQuad; duration: 250; }
            }
        }

        Rectangle
        {
            id: backFull;
            anchors.fill: parent;
            opacity: 0.0;
            radius: 2.0;

            color: "#F0F0F0";

            states: [
                State {
                    name: "mouseEntered"; when: mouseArea.containsMouse && root.checked;
                    PropertyChanges { target: backFull; color: "#FFFFFF"; opacity: 1.0; }
                },
                State {
                    name: "mouseExited"; when: !mouseArea.containsMouse && root.checked;
                    PropertyChanges { target: backFull; color: "#F0F0F0"; opacity: 0.5; }
                }
            ]

            transitions: [
                Transition {
                    NumberAnimation { property: "opacity"; easing.type: Easing.InOutQuad; duration: 250; }
                },
                Transition {
                    ColorAnimation { property: "color"; easing.type: Easing.InOutQuad; duration: 250; }
                }
            ]
        }

        Text {
            id: textBox;
            anchors.fill: parent;
            horizontalAlignment: Text.AlignLeft;
            verticalAlignment: Text.AlignVCenter;
            color: "black";

            textFormat: Text.PlainText;
            style: Text.Outline;
            styleColor: "white";
            font.pixelSize: 32;
            text: root.text;
        }
    }
}
