import QtQuick 2.0

Rectangle {
    id: titleOptions;
    color: "#A5FFFFFF";


    ListView {
        id: optionListView;

        model: ["a", "b", "c"]
    }
}
