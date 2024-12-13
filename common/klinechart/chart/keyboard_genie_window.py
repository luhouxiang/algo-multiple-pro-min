from PySide6 import QtGui, QtWidgets, QtCore

class KeyboardGenieWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口标志，使其成为子窗口，无标题栏和边框
        # self.setWindowFlags(QtCore.Qt.SubWindow | QtCore.Qt.FramelessWindowHint)
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # 设置窗口标志
        # self.setWindowFlags(
        #     QtCore.Qt.SubWindow |
        #     QtCore.Qt.Tool |
        #     QtCore.Qt.CustomizeWindowHint |
        #     QtCore.Qt.WindowDoesNotAcceptFocus |
        #     QtCore.Qt.WindowCloseButtonHint
        # )
        # 设置窗口标志，移除标题栏并确保窗口保持在父窗口前面
        # self.setWindowFlags(
        #     QtCore.Qt.Tool |
        #     QtCore.Qt.FramelessWindowHint |
        #     QtCore.Qt.WindowStaysOnTopHint |
        #     QtCore.Qt.WindowDoesNotAcceptFocus
        # )
        # self.setWindowFlags(
        #     QtCore.Qt.Tool |
        #     QtCore.Qt.FramelessWindowHint |
        #     QtCore.Qt.WindowStaysOnTopHint
        #     # 移除 QtCore.Qt.WindowDoesNotAcceptFocus
        # )
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        # 使窗口始终保持在父窗口的前面
        # self.setParent(parent, QtCore.Qt.Window)
        # 设置窗口属性，使其在父窗口前面
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        # 设置窗口大小策略
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # 创建布局
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # 输入框
        self.input_line_edit = QtWidgets.QLineEdit()
        self.input_line_edit.setPlaceholderText("请输入股票代码或名称")
        layout.addWidget(self.input_line_edit)

        # 匹配的股票代码列表
        self.matching_list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.matching_list_widget)

        # 设置列表控件的滚动条策略
        self.matching_list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.matching_list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # 创建一个临时的列表项来获取高度
        temp_item = QtWidgets.QListWidgetItem("示例文本")
        self.matching_list_widget.addItem(temp_item)
        item_height = self.matching_list_widget.sizeHintForRow(0)
        self.matching_list_widget.clear()  # 清除临时项

        # 计算显示6个列表项所需的高度
        visible_row_count = 6
        list_widget_height = item_height * visible_row_count

        # 设置列表控件的固定高度
        self.matching_list_widget.setFixedHeight(list_widget_height)

        self.setLayout(layout)
        self.hide()

        # # 安装事件过滤器
        # self.installEventFilter(self)
        # 连接键盘精灵的信号槽
        # 连接输入框的信号槽
        self.input_line_edit.textChanged.connect(self.on_input_text_changed)
        self.input_line_edit.returnPressed.connect(self.on_return_pressed)
        self.matching_list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)


    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            self.hide()
            self.parent().setFocus()
        elif key in (QtCore.Qt.Key_Up, QtCore.Qt.Key_Down):
            # 将方向键事件传递给列表框
            self.matching_list_widget.keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    # def eventFilter(self, obj, event):
    #     if event.type() == QtCore.QEvent.KeyPress:
    #         if event.key() == QtCore.Qt.Key_Escape:
    #             self.hide()
    #             return True
    #         else:
    #             # 将未处理的键盘事件传递给主窗口
    #             QtWidgets.QApplication.sendEvent(self.parent(), event)
    #             return True
    #     return super().eventFilter(obj, event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # 当键盘精灵窗口失去焦点时，隐藏窗口并将焦点返回给主窗口
        self.hide()
        self.parent().setFocus()

    def on_input_text_changed(self, text):
        # 调用父窗口的方法更新匹配列表
        self.parent().update_matching_list(text)

    def on_return_pressed(self):
        # 获取列表中选中的项
        selected_items = self.matching_list_widget.selectedItems()
        if selected_items:
            selected_stock_code = selected_items[0].data(QtCore.Qt.UserRole)
            print(f"按下回车选中股票代码：{selected_stock_code}")
            # 在这里加载股票数据并更新图表
            self.hide()
            self.parent().setFocus()
        else:
            # 如果没有选中项，且列表中有内容，默认选中第一项
            if self.matching_list_widget.count() > 0:
                item = self.matching_list_widget.item(0)
                selected_stock_code = item.data(QtCore.Qt.UserRole)
                print(f"按下回车默认选中第一项股票代码：{selected_stock_code}")
                # 在这里加载股票数据并更新图表
                self.hide()
                self.parent().setFocus()
            else:
                # 如果列表为空，可以根据需要处理
                print("没有匹配的股票代码")

    def on_item_double_clicked(self, item):
        # 双击列表项，处理选中的股票代码
        selected_stock_code = item.data(QtCore.Qt.UserRole)
        print(f"双击选中股票代码：{selected_stock_code}")
        # 在这里加载股票数据并更新图表
        self.hide()
        self.parent().setFocus()