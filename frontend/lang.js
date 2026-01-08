const translations = {
    en: {
        title: "RealEgo",
        nav_chat: "Chat",
        nav_profile: "Profile & Memory",
        nav_settings: "Settings",
        nav_logout: "Logout",
        chat_header: "Chat with RealEgo",
        toggle_log: "Toggle Status Log",
        status_ready: "Ready.",
        placeholder_message: "Type a message...",
        btn_send: "Send",
        profile_header: "Profile Settings",
        label_fullname: "Full Name",
        label_birthdate: "Birth Date",
        label_location: "Location",
        label_family: "Family Info",
        btn_save_profile: "Save Profile",
        upload_header: "Upload Documents (TOS)",
        btn_upload: "Upload",
        settings_header: "Settings",
        label_history_limit: "Chat History Limit (Number of messages to store/retrieve)",
        btn_save_settings: "Save Settings",
        thinking: "Thinking...",
        log_sending: "Sending message...",
        log_loading_profile: "Loading user profile...",
        log_profile_loaded: "Profile loaded.",
        log_searching_memories: "Searching relevant memories...",
        log_found_memories: "Found {n} relevant memories.",
        log_waiting_llm: "Constructing prompt and waiting for LLM...",
        log_llm_received: "LLM response received.",
        log_queueing_storage: "Queueing background memory storage...",
        log_tasks_queued: "All tasks queued. Done.",
        alert_session_expired: "Session expired. Please login again.",
        alert_profile_saved: "Profile saved!",
        alert_settings_saved: "Settings saved!",
        alert_upload_success: "Uploaded: {filename}",
        alert_upload_fail: "Upload failed",
        error_server: "Error communicating with server."
    },
    zh: {
        title: "RealEgo",
        nav_chat: "聊天",
        nav_profile: "档案与记忆",
        nav_settings: "设置",
        nav_logout: "退出登录",
        chat_header: "与 RealEgo 对话",
        toggle_log: "显示/隐藏日志",
        status_ready: "就绪。",
        placeholder_message: "输入消息...",
        btn_send: "发送",
        profile_header: "个人档案设置",
        label_fullname: "姓名",
        label_birthdate: "出生日期",
        label_location: "所在地",
        label_family: "家庭信息",
        btn_save_profile: "保存档案",
        upload_header: "上传文档 (TOS)",
        btn_upload: "上传",
        settings_header: "系统设置",
        label_history_limit: "历史记录加载数量",
        btn_save_settings: "保存设置",
        thinking: "思考中...",
        log_sending: "正在发送消息...",
        log_loading_profile: "正在加载用户档案...",
        log_profile_loaded: "档案加载完毕。",
        log_searching_memories: "正在搜索相关记忆...",
        log_found_memories: "找到 {n} 条相关记忆。",
        log_waiting_llm: "构建提示词并等待大模型...",
        log_llm_received: "收到大模型回复。",
        log_queueing_storage: "正在后台存储记忆...",
        log_tasks_queued: "所有任务已加入队列。完成。",
        alert_session_expired: "会话已过期，请重新登录。",
        alert_profile_saved: "档案已保存！",
        alert_settings_saved: "设置已保存！",
        alert_upload_success: "上传成功：{filename}",
        alert_upload_fail: "上传失败",
        error_server: "服务器通信错误。"
    }
};

let currentLang = localStorage.getItem('lang') || 'en';

function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    localStorage.setItem('lang', lang);
    applyTranslations();
}

function t(key, params = {}) {
    let text = translations[currentLang][key] || key;
    for (const [k, v] of Object.entries(params)) {
        text = text.replace(`{${k}}`, v);
    }
    return text;
}

function applyTranslations() {
    // Update active state of language buttons if we add them
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        // Handle placeholders for inputs
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            if (el.hasAttribute('placeholder')) {
                el.placeholder = t(key);
            }
        } else {
            // Check if element has children (like icons)
            if (el.children.length > 0) {
                // If it has icon, we need to preserve it. 
                // Simple heuristic: assume text is the last node or wrapped in span if we refactor.
                // Current HTML structure: <button><i class="..."></i> Text</button>
                // We should probably update the text node only.
                
                // Let's find the text node
                let textNode = null;
                for (let node of el.childNodes) {
                    if (node.nodeType === 3 && node.nodeValue.trim() !== '') {
                        textNode = node;
                        break;
                    }
                }
                if (textNode) {
                    textNode.nodeValue = ' ' + t(key);
                } else {
                     // Fallback for button with icon but no text node (or empty text node)
                     // e.g. <button><i class="..."></i></button> where text was removed or never there?
                     // But our HTML is <button><i...></i> Text</button>
                     // If text node is empty string (whitespace), it might be skipped by loop above if trim() check fails.
                     // Let's try to append a text node if none exists.
                     const newText = ' ' + t(key);
                     el.appendChild(document.createTextNode(newText));
                }
            } else {
                el.innerText = t(key);
            }
        }
    });

    // Also update the select dropdown if it exists
    const select = document.getElementById('lang-select');
    if (select) select.value = currentLang;
}
