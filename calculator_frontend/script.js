// 后端服务器地址
const API_BASE_URL = "http://127.0.0.1:8000";


// 获取页面上的元素
const display = document.getElementById("display");
const result = document.getElementById("result");
const message = document.getElementById("message");


// ------------------------------------
// 输入相关功能
// ------------------------------------


// 向输入框添加字符
function appendValue(value) {
    display.value += value;
}


// 清空输入框
function clearDisplay() {
    display.value = "";

    result.textContent = "计算结果：";

    message.textContent = "";
}


// 删除最后一个字符
function deleteLast() {
    display.value = display.value.slice(0, -1);
}


// ------------------------------------
// 计算功能
// ------------------------------------


async function calculate() {

    // 获取用户输入
    const expression = display.value.trim();

    // 如果没有输入
    if (expression === "") {
        message.textContent = "请输入表达式";
        return;
    }

    message.textContent = "";

    try {

        // 向 Python 后端发送 POST 请求
        const response = await fetch(
            `${API_BASE_URL}/api/calculate`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    expression: expression
                })
            }
        );


        // 获取后端返回的数据
        const data = await response.json();


        // 如果请求失败
        if (!response.ok) {

            message.textContent =
                data.detail || "计算失败";

            return;
        }


        // 显示结果
        result.textContent =
            `计算结果：${data.result}`;


        // 重新加载历史记录
        loadHistory();

    } catch (error) {

        message.textContent =
            "无法连接后端，请检查 Python 后端是否已经启动。";

    }
}


// ------------------------------------
// 获取历史记录
// ------------------------------------


async function loadHistory() {

    const historyList =
        document.getElementById("history-list");

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/history`
        );

        const history = await response.json();


        // 清空原来的内容
        historyList.innerHTML = "";


        // 如果没有历史
        if (history.length === 0) {

            historyList.textContent =
                "暂无历史记录";

            return;
        }


        // 显示每一条历史记录
        history.forEach(item => {

            // 整条记录
            const historyItem =
                document.createElement("div");

            historyItem.className =
                "history-item";


            // 左侧文字区域
            const content =
                document.createElement("div");

            content.className =
                "history-content";


            // 表达式和结果
            const expression =
                document.createElement("div");

            expression.className =
                "history-expression";

            expression.textContent =
                `${item.expression} = ${item.result}`;


            // 时间
            const time =
                document.createElement("div");

            time.className =
                "history-time";

            time.textContent =
                item.created_at;


            // 加入左侧区域
            content.appendChild(expression);

            content.appendChild(time);


            // 删除按钮
            const deleteButton =
                document.createElement("button");

            deleteButton.className =
                "delete-button";

            deleteButton.textContent =
                "删除";

            deleteButton.onclick =
                () => deleteHistory(item.id);


            // 放入整条记录
            historyItem.appendChild(content);

            historyItem.appendChild(deleteButton);


            // 放入历史列表
            historyList.appendChild(historyItem);
        });

    } catch (error) {

        historyList.textContent =
            "无法获取历史记录";

    }
}


// ------------------------------------
// 删除历史记录
// ------------------------------------


async function deleteHistory(id) {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/history/${id}`,
            {
                method: "DELETE"
            }
        );


        if (!response.ok) {

            alert("删除失败");

            return;
        }


        // 删除成功以后重新读取数据库
        loadHistory();

    } catch (error) {

        alert("无法连接后端");

    }
}


// ------------------------------------
// 页面打开时自动获取历史记录
// ------------------------------------


loadHistory();


// 按 Enter 也可以计算
display.addEventListener(
    "keydown",

    function(event) {

        if (event.key === "Enter") {
            calculate();
        }

    }
);