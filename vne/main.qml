import QtQuick 2.8

Item {
    property string text;
    anchors.fill: parent;

    PageTitle
    {
        id: titleScreen;
        anchors.fill: parent;
    }

    PageOptions
    {
        id: titleOptions;

        anchors.right: parent.right;
        anchors.rightMargin: 32;
        anchors.bottom: parent.bottom;
        anchors.bottomMargin: 32;

        width: 1280 - 384 - 32;
        height: 720 - 96;
    }
}
