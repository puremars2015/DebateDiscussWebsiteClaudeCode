// API 配置
const API_BASE_URL = 'http://localhost:5000/api';

// 獲取本地儲存的 token
function getToken() {
    return localStorage.getItem('auth_token');
}

// 設置 token
function setToken(token) {
    localStorage.setItem('auth_token', token);
}

// 清除 token
function clearToken() {
    localStorage.removeItem('auth_token');
}

// 獲取當前用戶
function getCurrentUser() {
    const userStr = localStorage.getItem('current_user');
    return userStr ? JSON.parse(userStr) : null;
}

// 設置當前用戶
function setCurrentUser(user) {
    localStorage.setItem('current_user', JSON.stringify(user));
}

// 清除當前用戶
function clearCurrentUser() {
    localStorage.removeItem('current_user');
}

// 通用 API 請求函數
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = getToken();

    const headers = {
        ...options.headers
    };

    // 只在有 body 時添加 Content-Type
    if (options.body) {
        headers['Content-Type'] = 'application/json';
    }

    // 只在有 token 時添加 Authorization
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const fetchOptions = {
        method: options.method || 'GET',
        headers: headers
    };

    // 只在有 body 的情況下添加
    if (options.body) {
        fetchOptions.body = options.body;
    }

    try {
        console.log(`[API] ${fetchOptions.method} ${url}`, fetchOptions.headers);
        const response = await fetch(url, fetchOptions);

        const data = await response.json();

        if (!response.ok) {
            console.error(`[API] Error ${response.status}:`, data);
            throw new Error(data.error || 'Request failed');
        }

        console.log(`[API] Success:`, data);
        return data;
    } catch (error) {
        console.error('[API] Request Error:', error);
        throw error;
    }
}

// API 方法

// 認證相關
const AuthAPI = {
    async getLoginUrl() {
        return await apiRequest('/auth/login');
    },

    async verify() {
        return await apiRequest('/auth/verify');
    },

    logout() {
        clearToken();
        clearCurrentUser();
        window.location.href = '/pages/login.html';
    }
};

// 用戶相關
const UserAPI = {
    async getCurrentUser() {
        return await apiRequest('/users/me');
    },

    async getUser(userId) {
        return await apiRequest(`/users/${userId}`);
    },

    async getUserMatches(userId) {
        return await apiRequest(`/users/${userId}/matches`);
    }
};

// 話題相關
const TopicAPI = {
    async getTopics(status = 'approved') {
        return await apiRequest(`/topics?status=${status}`);
    },

    async getTopic(topicId) {
        return await apiRequest(`/topics/${topicId}`);
    },

    async applyTopic(topicData) {
        return await apiRequest('/topics/apply', {
            method: 'POST',
            body: JSON.stringify(topicData)
        });
    }
};

// 辯論相關
const DebateAPI = {
    async getDebates(status = 'ONGOING') {
        return await apiRequest(`/debates?status=${status}`);
    },

    async getDebate(debateId) {
        return await apiRequest(`/debates/${debateId}`);
    },

    async createDebate(debateData) {
        return await apiRequest('/debates/create', {
            method: 'POST',
            body: JSON.stringify(debateData)
        });
    }
};

// 回合相關
const RoundAPI = {
    async getRound(roundId) {
        return await apiRequest(`/rounds/${roundId}`);
    },

    async submitProsStatement(roundId, statement) {
        return await apiRequest(`/rounds/${roundId}/pros_statement`, {
            method: 'POST',
            body: JSON.stringify({ statement })
        });
    },

    async submitConsQuestions(roundId, questions) {
        return await apiRequest(`/rounds/${roundId}/cons_questions`, {
            method: 'POST',
            body: JSON.stringify({ questions })
        });
    },

    async submitProsReply(roundId, reply) {
        return await apiRequest(`/rounds/${roundId}/pros_reply`, {
            method: 'POST',
            body: JSON.stringify({ reply })
        });
    },

    async submitConsStatement(roundId, statement) {
        return await apiRequest(`/rounds/${roundId}/cons_statement`, {
            method: 'POST',
            body: JSON.stringify({ statement })
        });
    },

    async submitProsQuestions(roundId, questions) {
        return await apiRequest(`/rounds/${roundId}/pros_questions`, {
            method: 'POST',
            body: JSON.stringify({ questions })
        });
    },

    async submitConsReply(roundId, reply) {
        return await apiRequest(`/rounds/${roundId}/cons_reply`, {
            method: 'POST',
            body: JSON.stringify({ reply })
        });
    }
};

// 投票相關
const VoteAPI = {
    async submitVote(roundId, sideVoted) {
        return await apiRequest(`/votes/${roundId}/vote`, {
            method: 'POST',
            body: JSON.stringify({ side_voted: sideVoted })
        });
    },

    async getResults(roundId) {
        return await apiRequest(`/votes/${roundId}/results`);
    }
};

// 排行榜相關
const RankingAPI = {
    async getRanking() {
        return await apiRequest('/ranking');
    }
};

// 管理員相關
const AdminAPI = {
    async getPendingTopics() {
        return await apiRequest('/admin/topics/pending');
    },

    async approveTopic(topicId) {
        return await apiRequest(`/admin/topics/${topicId}/approve`, {
            method: 'POST'
        });
    },

    async rejectTopic(topicId) {
        return await apiRequest(`/admin/topics/${topicId}/reject`, {
            method: 'POST'
        });
    },

    async forceEndDebate(debateId, winnerId) {
        return await apiRequest(`/admin/debates/${debateId}/force_end`, {
            method: 'POST',
            body: JSON.stringify({ winner_id: winnerId })
        });
    },

    async setAdmin(userId, isAdmin) {
        return await apiRequest(`/admin/users/${userId}/set_admin`, {
            method: 'POST',
            body: JSON.stringify({ is_admin: isAdmin })
        });
    },

    async assignJudge(debateId, userId) {
        return await apiRequest('/admin/judges/assign', {
            method: 'POST',
            body: JSON.stringify({ debate_id: debateId, user_id: userId })
        });
    }
};
