const API = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("token");
}

function setToken(token) {
    localStorage.setItem("token", token);
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

function authHeaders(json = false) {
    const headers = {};

    const token = getToken();
    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }

    if (json) {
        headers["Content-Type"] = "application/json";
    }

    return headers;
}

function getErrorMessage(data) {
    if (!data) {
        return "Request failed";
    }

    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data.detail)) {
        return data.detail
            .map((item) => {
                const field = Array.isArray(item.loc) ? item.loc.join(" -> ") : "field";
                return `${field}: ${item.msg}`;
            })
            .join("\n");
    }

    return "Request failed";
}

async function handleResponse(response) {
    let data = {};

    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
        data = await response.json();
    }

    if (!response.ok) {
        throw new Error(getErrorMessage(data));
    }

    return data;
}

function requireValue(value, message) {
    if (!value || !String(value).trim()) {
        throw new Error(message);
    }
}

function requireAuthOnPrivatePages() {
    const publicPaths = ["/"];
    const currentPath = window.location.pathname;

    if (!publicPaths.includes(currentPath) && !getToken()) {
        window.location.href = "/";
    }
}

async function login() {
    try {
        const email = document.getElementById("email")?.value.trim();
        const password = document.getElementById("password")?.value;

        requireValue(email, "Введите email");
        requireValue(password, "Введите пароль");

        const response = await fetch(API + "/auth/login", {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({ email, password })
        });

        const data = await handleResponse(response);
        setToken(data.access_token);
        window.location.href = "/dashboard";
    } catch (error) {
        alert(error.message);
    }
}

async function register() {
    try {
        const email = document.getElementById("reg_email")?.value.trim();
        const password = document.getElementById("reg_password")?.value;
        const full_name = document.getElementById("reg_name")?.value.trim();

        requireValue(email, "Введите email");
        requireValue(password, "Введите пароль");
        requireValue(full_name, "Введите имя");

        const response = await fetch(API + "/auth/register", {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({ email, password, full_name })
        });

        await handleResponse(response);
        alert("Registered successfully");
    } catch (error) {
        alert(error.message);
    }
}

async function loadCurrentUser() {
    const block = document.getElementById("user-info");
    if (!block || !getToken()) return;

    try {
        const response = await fetch(API + "/auth/me", {
            headers: authHeaders()
        });

        const user = await handleResponse(response);
        block.innerHTML = `
            <div class="card">
                <p><strong>ID:</strong> ${user.id}</p>
                <p><strong>Email:</strong> ${user.email}</p>
                <p><strong>Name:</strong> ${user.full_name}</p>
                <p><strong>Role:</strong> ${user.role}</p>
                <p><strong>Team ID:</strong> ${user.team_id ?? "—"}</p>
            </div>
        `;
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function loadTasks() {
    const div = document.getElementById("tasks");
    if (!div) return;

    try {
        const response = await fetch(API + "/tasks/", {
            headers: authHeaders()
        });

        const tasks = await handleResponse(response);

        div.innerHTML = "";
        tasks.forEach(task => {
            div.innerHTML += `
                <div class="item">
                    <p><strong>ID:</strong> ${task.id}</p>
                    <p><strong>Title:</strong> ${task.title}</p>
                    <p><strong>Status:</strong> ${task.status}</p>
                    <p><strong>Executor ID:</strong> ${task.executor_id}</p>
                    <p><strong>Deadline:</strong> ${task.deadline ?? "—"}</p>
                </div>
            `;
        });

        if (tasks.length === 0) {
            div.innerHTML = `<p>Нет задач</p>`;
        }
    } catch (error) {
        div.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function createTask() {
    try {
        const title = document.getElementById("title")?.value.trim();
        const description = document.getElementById("description")?.value.trim() || null;
        const deadline = document.getElementById("deadline")?.value || null;
        const executorIdValue = document.getElementById("executor_id")?.value.trim();

        requireValue(title, "Введите название задачи");
        requireValue(executorIdValue, "Введите ID исполнителя");

        const executor_id = parseInt(executorIdValue, 10);
        if (Number.isNaN(executor_id)) {
            throw new Error("Executor ID должен быть числом");
        }

        const response = await fetch(API + "/tasks/", {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({
                title,
                description,
                deadline,
                executor_id
            })
        });

        await handleResponse(response);
        alert("Task created");
        loadTasks();
    } catch (error) {
        alert(error.message);
    }
}

async function createTeam() {
    try {
        const name = document.getElementById("team_name")?.value.trim();
        requireValue(name, "Введите название команды");

        const response = await fetch(API + "/teams/", {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({ name })
        });

        const data = await handleResponse(response);
        alert(`Team created. Code: ${data.code}`);
    } catch (error) {
        alert(error.message);
    }
}

async function joinTeam() {
    try {
        const code = document.getElementById("team_code")?.value.trim();
        requireValue(code, "Введите код команды");

        const response = await fetch(API + "/teams/join", {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({ code })
        });

        const data = await handleResponse(response);
        alert(data.detail);
    } catch (error) {
        alert(error.message);
    }
}

async function loadTeamMembers() {
    const block = document.getElementById("team-members");
    if (!block) return;

    try {
        const response = await fetch(API + "/teams/members", {
            headers: authHeaders()
        });

        const users = await handleResponse(response);
        block.innerHTML = "";

        users.forEach(user => {
            block.innerHTML += `
                <div class="item">
                    <p><strong>ID:</strong> ${user.id}</p>
                    <p><strong>Name:</strong> ${user.full_name}</p>
                    <p><strong>Email:</strong> ${user.email}</p>
                    <p><strong>Role:</strong> ${user.role}</p>
                </div>
            `;
        });

        if (users.length === 0) {
            block.innerHTML = `<p>Нет участников</p>`;
        }
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function changeUserRole() {
    try {
        const userIdValue = document.getElementById("role_user_id")?.value.trim();
        const role = document.getElementById("new_role")?.value;

        requireValue(userIdValue, "Введите ID пользователя");
        requireValue(role, "Выберите роль");

        const user_id = parseInt(userIdValue, 10);
        if (Number.isNaN(user_id)) {
            throw new Error("User ID должен быть числом");
        }

        const response = await fetch(API + "/teams/role", {
            method: "PATCH",
            headers: authHeaders(true),
            body: JSON.stringify({ user_id, role })
        });

        const data = await handleResponse(response);
        alert(data.detail);
    } catch (error) {
        alert(error.message);
    }
}

async function removeUserFromTeam() {
    try {
        const userIdValue = document.getElementById("remove_user_id")?.value.trim();
        requireValue(userIdValue, "Введите ID пользователя");

        const user_id = parseInt(userIdValue, 10);
        if (Number.isNaN(user_id)) {
            throw new Error("User ID должен быть числом");
        }

        const response = await fetch(API + "/teams/" + user_id, {
            method: "DELETE",
            headers: authHeaders()
        });

        const data = await handleResponse(response);
        alert(data.detail);
    } catch (error) {
        alert(error.message);
    }
}

async function createMeeting() {
    try {
        const title = document.getElementById("meeting_title")?.value.trim();
        const description = document.getElementById("meeting_description")?.value.trim() || null;
        const start_time = document.getElementById("meeting_start")?.value;
        const end_time = document.getElementById("meeting_end")?.value;
        const rawIds = document.getElementById("participant_ids")?.value.trim() || "";

        requireValue(title, "Введите название встречи");
        requireValue(start_time, "Введите дату начала");
        requireValue(end_time, "Введите дату окончания");

        const participant_ids = rawIds
            ? rawIds.split(",").map(x => parseInt(x.trim(), 10)).filter(x => !Number.isNaN(x))
            : [];

        const response = await fetch(API + "/meetings/", {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({
                title,
                description,
                start_time,
                end_time,
                participant_ids
            })
        });

        await handleResponse(response);
        alert("Meeting created");
        loadMeetings();
    } catch (error) {
        alert(error.message);
    }
}

async function loadMeetings() {
    const block = document.getElementById("meetings-list");
    if (!block) return;

    try {
        const response = await fetch(API + "/meetings/my", {
            headers: authHeaders()
        });

        const meetings = await handleResponse(response);
        block.innerHTML = "";

        meetings.forEach(meeting => {
            block.innerHTML += `
                <div class="item">
                    <p><strong>ID:</strong> ${meeting.id}</p>
                    <p><strong>Title:</strong> ${meeting.title}</p>
                    <p><strong>Description:</strong> ${meeting.description ?? "—"}</p>
                    <p><strong>Start:</strong> ${meeting.start_time}</p>
                    <p><strong>End:</strong> ${meeting.end_time}</p>
                    <button onclick="deleteMeeting(${meeting.id})">Delete</button>
                </div>
            `;
        });

        if (meetings.length === 0) {
            block.innerHTML = `<p>Нет встреч</p>`;
        }
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function deleteMeeting(meetingId) {
    try {
        const response = await fetch(API + "/meetings/" + meetingId, {
            method: "DELETE",
            headers: authHeaders()
        });

        if (!response.ok && response.status !== 204) {
            await handleResponse(response);
        }

        alert("Meeting deleted");
        loadMeetings();
    } catch (error) {
        alert(error.message);
    }
}

async function createEvaluation() {
    try {
        const taskIdValue = document.getElementById("evaluation_task_id")?.value.trim();
        const scoreValue = document.getElementById("evaluation_score")?.value.trim();
        const comment = document.getElementById("evaluation_comment")?.value.trim() || null;

        requireValue(taskIdValue, "Введите ID задачи");
        requireValue(scoreValue, "Введите оценку");

        const task_id = parseInt(taskIdValue, 10);
        const score = parseInt(scoreValue, 10);

        if (Number.isNaN(task_id)) {
            throw new Error("Task ID должен быть числом");
        }

        if (Number.isNaN(score) || score < 1 || score > 5) {
            throw new Error("Оценка должна быть числом от 1 до 5");
        }

        const response = await fetch(API + "/evaluations/", {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({ task_id, score, comment })
        });

        await handleResponse(response);
        alert("Evaluation created");
        loadMyEvaluations();
    } catch (error) {
        alert(error.message);
    }
}

async function loadMyEvaluations() {
    const block = document.getElementById("evaluations-list");
    if (!block) return;

    try {
        const response = await fetch(API + "/evaluations/my", {
            headers: authHeaders()
        });

        const evaluations = await handleResponse(response);
        block.innerHTML = "";

        evaluations.forEach(item => {
            block.innerHTML += `
                <div class="item">
                    <p><strong>ID:</strong> ${item.id}</p>
                    <p><strong>Task ID:</strong> ${item.task_id}</p>
                    <p><strong>Score:</strong> ${item.score}</p>
                    <p><strong>Comment:</strong> ${item.comment ?? "—"}</p>
                    <p><strong>Created:</strong> ${item.created_at}</p>
                </div>
            `;
        });

        if (evaluations.length === 0) {
            block.innerHTML = `<p>Нет оценок</p>`;
        }
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function loadAverageScore() {
    const block = document.getElementById("average-score");
    if (!block) return;

    try {
        const response = await fetch(API + "/evaluations/average", {
            headers: authHeaders()
        });

        const data = await handleResponse(response);
        block.innerHTML = `<p><strong>Average score:</strong> ${data.average_score ?? "No data"}</p>`;
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function loadAverageScoreByPeriod() {
    const block = document.getElementById("average-score-period");
    if (!block) return;

    try {
        const date_from = document.getElementById("avg_date_from")?.value;
        const date_to = document.getElementById("avg_date_to")?.value;

        requireValue(date_from, "Введите начальную дату");
        requireValue(date_to, "Введите конечную дату");

        const url = new URL(API + "/evaluations/average-by-period");
        url.searchParams.append("date_from", date_from);
        url.searchParams.append("date_to", date_to);

        const response = await fetch(url, {
            headers: authHeaders()
        });

        const data = await handleResponse(response);
        block.innerHTML = `<p><strong>Average score by period:</strong> ${data.average_score ?? "No data"}</p>`;
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function loadCalendarDay() {
    const block = document.getElementById("calendar-day-result");
    if (!block) return;

    try {
        const day = document.getElementById("calendar_day")?.value;
        requireValue(day, "Выберите дату");

        const url = new URL(API + "/calendar/day");
        url.searchParams.append("day", day);

        const response = await fetch(url, {
            headers: authHeaders()
        });

        const data = await handleResponse(response);
        block.innerHTML = `
            <div class="item">
                <p><strong>Day:</strong> ${data.day}</p>
                <pre>${JSON.stringify(data.items, null, 2)}</pre>
            </div>
        `;
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function loadCalendarMonth() {
    const block = document.getElementById("calendar-month-result");
    if (!block) return;

    try {
        const year = document.getElementById("calendar_year")?.value.trim();
        const month = document.getElementById("calendar_month")?.value.trim();

        requireValue(year, "Введите год");
        requireValue(month, "Введите месяц");

        const url = new URL(API + "/calendar/month");
        url.searchParams.append("year", year);
        url.searchParams.append("month", month);

        const response = await fetch(url, {
            headers: authHeaders()
        });

        const data = await handleResponse(response);
        block.innerHTML = `
            <div class="item">
                <p><strong>Year:</strong> ${data.year}</p>
                <p><strong>Month:</strong> ${data.month}</p>
                <pre>${JSON.stringify(data.days, null, 2)}</pre>
            </div>
        `;
    } catch (error) {
        block.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    requireAuthOnPrivatePages();
    loadCurrentUser();

    if (document.getElementById("tasks")) {
        loadTasks();
    }

    if (document.getElementById("team-members")) {
        loadTeamMembers();
    }

    if (document.getElementById("meetings-list")) {
        loadMeetings();
    }

    if (document.getElementById("evaluations-list")) {
        loadMyEvaluations();
    }
});