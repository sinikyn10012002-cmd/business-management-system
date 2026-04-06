const API = "http://127.0.0.1:8000";
const STATUS_LABELS = {
  open: "Открыто",
  in_progress: "В работе",
  done: "Выполнено",
};

function getToken() {
  return localStorage.getItem("access_token") || "";
}

function setToken(token) {
  if (token) localStorage.setItem("access_token", token);
}

function clearToken() {
  localStorage.removeItem("access_token");
}

function qs(selector, root = document) {
  return root.querySelector(selector);
}

function qsa(selector, root = document) {
  return [...root.querySelectorAll(selector)];
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function fmtDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("ru-RU", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function dateInputValue(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function showMessage(text, type = "notice") {
  const box = qs("#global-message");
  if (!box) return;
  box.className = type;
  box.textContent = text;
  box.classList.remove("hidden");
}

function clearMessage() {
  const box = qs("#global-message");
  if (!box) return;
  box.classList.add("hidden");
  box.textContent = "";
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API}${path}`, { ...options, headers });

  if (response.status === 204) return null;

  const raw = await response.text();
  let data;
  try {
    data = raw ? JSON.parse(raw) : null;
  } catch {
    data = raw;
  }

  if (!response.ok) {
    const message = data?.detail || data?.message || `HTTP ${response.status}`;
    throw new Error(message);
  }

  return data;
}

async function loadMe() {
  return api("/auth/me");
}

function ensureAuthPageAccess() {
  if (!getToken()) window.location.href = "/";
}

function renderSidebar(active) {
  const menu = [
    ["/dashboard", "Обзор", "dashboard"],
    ["/teams-page", "Команды", "teams"],
    ["/tasks-page", "Задачи", "tasks"],
    ["/meetings-page", "Встречи", "meetings"],
    ["/evaluations-page", "Оценки", "evaluations"],
    ["/calendar-page", "Календарь", "calendar"],
  ];
  const nav = qs("#main-nav");
  if (!nav) return;
  nav.innerHTML = menu
    .map(([href, label, key]) => `<a class="${active === key ? "active" : ""}" href="${href}">${label}</a>`)
    .join("");
}

function attachLogout() {
  const btn = qs("#logout-btn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    clearToken();
    window.location.href = "/";
  });
}

async function initAuthPage() {
  if (getToken()) {
    try {
      await loadMe();
      window.location.href = "/dashboard";
      return;
    } catch {
      clearToken();
    }
  }

  const loginTab = qs("#tab-login");
  const registerTab = qs("#tab-register");
  const loginForm = qs("#login-form");
  const registerForm = qs("#register-form");

  function switchTab(kind) {
    const isLogin = kind === "login";
    loginForm.classList.toggle("hidden", !isLogin);
    registerForm.classList.toggle("hidden", isLogin);
    loginTab.classList.toggle("inactive", !isLogin);
    registerTab.classList.toggle("inactive", isLogin);
    clearMessage();
  }

  loginTab.addEventListener("click", () => switchTab("login"));
  registerTab.addEventListener("click", () => switchTab("register"));

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearMessage();
    try {
      const payload = {
        email: qs("#login-email").value.trim(),
        password: qs("#login-password").value,
      };
      const data = await api("/auth/login", { method: "POST", body: JSON.stringify(payload) });
      setToken(data.access_token);
      window.location.href = "/dashboard";
    } catch (err) {
      showMessage(err.message, "error");
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearMessage();
    try {
      const payload = {
        email: qs("#register-email").value.trim(),
        password: qs("#register-password").value,
        full_name: qs("#register-full-name").value.trim(),
      };
      await api("/auth/register", { method: "POST", body: JSON.stringify(payload) });
      showMessage("Регистрация успешна. Теперь войдите в аккаунт.");
      switchTab("login");
      qs("#login-email").value = payload.email;
    } catch (err) {
      showMessage(err.message, "error");
    }
  });
}

async function initDashboardPage() {
  ensureAuthPageAccess();
  renderSidebar("dashboard");
  attachLogout();
  try {
    const me = await loadMe();
    qs("#profile-summary").innerHTML = `
      <div class="kpi"><div class="muted">Имя</div><div class="value" style="font-size:22px">${escapeHtml(me.full_name || "—")}</div></div>
      <div class="kpi"><div class="muted">Email</div><div class="value" style="font-size:22px">${escapeHtml(me.email)}</div></div>
      <div class="kpi"><div class="muted">Роль</div><div class="value" style="font-size:22px">${escapeHtml(me.role)}</div></div>
      <div class="kpi"><div class="muted">Команда ID</div><div class="value" style="font-size:22px">${escapeHtml(me.team_id ?? "—")}</div></div>
    `;
    qs("#profile-full-name").value = me.full_name || "";
    qs("#profile-email").value = me.email || "";

    qs("#profile-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      clearMessage();
      try {
        const payload = {
          full_name: qs("#profile-full-name").value.trim(),
          email: qs("#profile-email").value.trim(),
        };
        const updated = await api("/auth/me", { method: "PATCH", body: JSON.stringify(payload) });
        showMessage("Профиль обновлён");
        qs("#profile-role").textContent = updated.role;
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    qs("#delete-account-btn").addEventListener("click", async () => {
      if (!confirm("Удалить аккаунт без восстановления?")) return;
      try {
        await api("/auth/me", { method: "DELETE" });
        clearToken();
        window.location.href = "/";
      } catch (err) {
        showMessage(err.message, "error");
      }
    });
  } catch (err) {
    clearToken();
    window.location.href = "/";
  }
}

async function initTeamsPage() {
  ensureAuthPageAccess();
  renderSidebar("teams");
  attachLogout();
  try {
    const me = await loadMe();
    qs("#current-role").textContent = me.role;
    qs("#current-team").textContent = me.team_id ?? "—";

    async function refreshMembers() {
      try {
        const members = await api("/teams/members");
        qs("#members-list").innerHTML = members.map((user) => `
          <div class="card">
            <div class="row">
              <div>
                <h3>${escapeHtml(user.full_name || user.email)}</h3>
                <div class="muted">${escapeHtml(user.email)}</div>
              </div>
              <div><span class="badge">${escapeHtml(user.role)}</span></div>
              <div><span class="badge">ID ${escapeHtml(user.id)}</span></div>
            </div>
            ${me.role === "admin" ? `
            <div class="row">
              <div>
                <label>Новая роль</label>
                <select data-role-user-id="${user.id}">
                  <option value="user">user</option>
                  <option value="manager">manager</option>
                </select>
              </div>
            </div>
            <div class="row actions">
              <button class="small secondary" data-change-role="${user.id}">Изменить роль</button>
              <button class="small danger" data-remove-user="${user.id}">Удалить из команды</button>
            </div>` : ""}
          </div>
        `).join("");

        qsa("[data-change-role]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const userId = Number(btn.dataset.changeRole);
            const role = qs(`[data-role-user-id="${userId}"]`).value;
            try {
              await api("/teams/role", {
                method: "PATCH",
                body: JSON.stringify({ user_id: userId, role }),
              });
              showMessage("Роль обновлена");
              refreshMembers();
            } catch (err) {
              showMessage(err.message, "error");
            }
          });
        });

        qsa("[data-remove-user]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const userId = Number(btn.dataset.removeUser);
            if (!confirm("Убрать пользователя из команды?")) return;
            try {
              await api(`/teams/${userId}`, { method: "DELETE" });
              showMessage("Пользователь удалён из команды");
              refreshMembers();
            } catch (err) {
              showMessage(err.message, "error");
            }
          });
        });
      } catch (err) {
        qs("#members-list").innerHTML = `<div class="error">${escapeHtml(err.message)}</div>`;
      }
    }

    qs("#join-team-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api("/teams/join", {
          method: "POST",
          body: JSON.stringify({ code: qs("#team-code").value.trim() }),
        });
        showMessage("Вы присоединились к команде");
        refreshMembers();
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    qs("#create-team-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const team = await api("/teams/", {
          method: "POST",
          body: JSON.stringify({ name: qs("#team-name").value.trim() }),
        });
        showMessage(`Команда создана. Код: ${team.code}`);
        qs("#created-team-result").textContent = `ID: ${team.id}, код: ${team.code}`;
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    if (me.role !== "admin") {
      qs("#create-team-panel").classList.add("hidden");
      qs("#manage-members-note").textContent = "Назначение ролей и удаление доступны только админу команды.";
    }

    await refreshMembers();
  } catch {
    clearToken();
    window.location.href = "/";
  }
}

async function initTasksPage() {
  ensureAuthPageAccess();
  renderSidebar("tasks");
  attachLogout();
  try {
    const me = await loadMe();
    if (me.role !== "manager") qs("#create-task-panel").classList.add("hidden");

    async function loadTasks() {
      try {
        const tasks = await api("/tasks/");
        const list = qs("#tasks-list");
        list.innerHTML = tasks.map((task) => `
          <div class="card">
            <div class="row">
              <div>
                <h3>${escapeHtml(task.title)}</h3>
                <div class="muted">${escapeHtml(task.description || "Без описания")}</div>
              </div>
              <div><span class="badge ${task.status}">${STATUS_LABELS[task.status] || task.status}</span></div>
            </div>
            <div class="row">
              <div class="muted">ID: ${task.id}</div>
              <div class="muted">Дедлайн: ${fmtDate(task.deadline)}</div>
              <div class="muted">Исполнитель ID: ${escapeHtml(task.executor_id)}</div>
              <div class="muted">Автор ID: ${escapeHtml(task.author_id)}</div>
            </div>
            <div class="row">
              <div>
                <label>Сменить статус</label>
                <select data-status-select="${task.id}">
                  <option value="open" ${task.status === "open" ? "selected" : ""}>Открыто</option>
                  <option value="in_progress" ${task.status === "in_progress" ? "selected" : ""}>В работе</option>
                  <option value="done" ${task.status === "done" ? "selected" : ""}>Выполнено</option>
                </select>
              </div>
              <div>
                <label>Новый исполнитель ID</label>
                <input data-edit-executor="${task.id}" type="number" value="${task.executor_id}">
              </div>
              <div>
                <label>Новый дедлайн</label>
                <input data-edit-deadline="${task.id}" type="datetime-local" value="${dateInputValue(task.deadline)}">
              </div>
            </div>
            <div class="row">
              <div>
                <label>Новый заголовок</label>
                <input data-edit-title="${task.id}" value="${escapeHtml(task.title)}">
              </div>
              <div>
                <label>Описание</label>
                <input data-edit-description="${task.id}" value="${escapeHtml(task.description || "")}">
              </div>
            </div>
            <div class="row actions">
              <button class="small warning" data-update-task="${task.id}">Обновить задачу</button>
              <button class="small success" data-change-status="${task.id}">Применить статус</button>
              <button class="small secondary" data-load-comments="${task.id}">Комментарии</button>
              <button class="small danger" data-delete-task="${task.id}">Удалить</button>
            </div>
            <div id="comments-box-${task.id}" class="stack hidden"></div>
          </div>
        `).join("");

        qsa("[data-change-status]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const taskId = btn.dataset.changeStatus;
            const value = qs(`[data-status-select="${taskId}"]`).value;
            try {
              await api(`/tasks/${taskId}/status?status_value=${encodeURIComponent(value)}`, { method: "PATCH" });
              showMessage("Статус обновлён");
              loadTasks();
            } catch (err) {
              showMessage(err.message, "error");
            }
          });
        });

        qsa("[data-update-task]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const taskId = btn.dataset.updateTask;
            const payload = {
              title: qs(`[data-edit-title="${taskId}"]`).value.trim(),
              description: qs(`[data-edit-description="${taskId}"]`).value.trim(),
              executor_id: Number(qs(`[data-edit-executor="${taskId}"]`).value),
              deadline: qs(`[data-edit-deadline="${taskId}"]`).value || null,
            };
            try {
              await api(`/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify(payload) });
              showMessage("Задача обновлена");
              loadTasks();
            } catch (err) {
              showMessage(err.message, "error");
            }
          });
        });

        qsa("[data-delete-task]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const taskId = btn.dataset.deleteTask;
            if (!confirm("Удалить задачу?")) return;
            try {
              await api(`/tasks/${taskId}`, { method: "DELETE" });
              showMessage("Задача удалена");
              loadTasks();
            } catch (err) {
              showMessage(err.message, "error");
            }
          });
        });

        qsa("[data-load-comments]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const taskId = btn.dataset.loadComments;
            const box = qs(`#comments-box-${taskId}`);
            box.classList.remove("hidden");
            try {
              const comments = await api(`/tasks/${taskId}/comments`);
              box.innerHTML = `
                <div class="panel">
                  <div class="stack">
                    <div class="row"><strong>Комментарии к задаче #${taskId}</strong></div>
                    <div class="list">
                      ${comments.length ? comments.map((comment) => `
                        <div class="comment">
                          <div>${escapeHtml(comment.text)}</div>
                          <div class="muted">Пользователь: ${escapeHtml(comment.user_id)} · ${fmtDate(comment.created_at)}</div>
                        </div>
                      `).join("") : `<div class="muted">Комментариев нет</div>`}
                    </div>
                    <form data-comment-form="${taskId}" class="stack">
                      <div>
                        <label>Новый комментарий</label>
                        <textarea data-comment-text="${taskId}" placeholder="Введите сообщение"></textarea>
                      </div>
                      <div class="row actions"><button class="small">Отправить</button></div>
                    </form>
                  </div>
                </div>
              `;
              qs(`[data-comment-form="${taskId}"]`).addEventListener("submit", async (e) => {
                e.preventDefault();
                try {
                  await api(`/tasks/${taskId}/comments`, {
                    method: "POST",
                    body: JSON.stringify({ text: qs(`[data-comment-text="${taskId}"]`).value.trim() }),
                  });
                  showMessage("Комментарий добавлен");
                  btn.click();
                } catch (err) {
                  showMessage(err.message, "error");
                }
              });
            } catch (err) {
              box.innerHTML = `<div class="error">${escapeHtml(err.message)}</div>`;
            }
          });
        });
      } catch (err) {
        qs("#tasks-list").innerHTML = `<div class="error">${escapeHtml(err.message)}</div>`;
      }
    }

    qs("#create-task-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const payload = {
          title: qs("#task-title").value.trim(),
          description: qs("#task-description").value.trim(),
          deadline: qs("#task-deadline").value || null,
          executor_id: Number(qs("#task-executor-id").value),
        };
        await api("/tasks/", { method: "POST", body: JSON.stringify(payload) });
        showMessage("Задача создана");
        e.target.reset();
        loadTasks();
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    await loadTasks();
  } catch {
    clearToken();
    window.location.href = "/";
  }
}

async function initMeetingsPage() {
  ensureAuthPageAccess();
  renderSidebar("meetings");
  attachLogout();
  try {
    await loadMe();

    async function loadMeetings() {
      try {
        const meetings = await api("/meetings/my");
        qs("#meetings-list").innerHTML = meetings.map((meeting) => `
          <div class="card">
            <div class="row">
              <div>
                <h3>${escapeHtml(meeting.title)}</h3>
                <div class="muted">${escapeHtml(meeting.description || "Без описания")}</div>
              </div>
              <div><span class="badge">ID ${meeting.id}</span></div>
            </div>
            <div class="row">
              <div class="muted">Начало: ${fmtDate(meeting.start_time)}</div>
              <div class="muted">Конец: ${fmtDate(meeting.end_time)}</div>
              <div class="muted">Организатор: ${escapeHtml(meeting.organizer_id)}</div>
            </div>
            <div class="muted">Участники: ${(meeting.participants || []).map((p) => p.id ?? p).join(", ") || "—"}</div>
            <div class="row actions"><button class="small danger" data-cancel-meeting="${meeting.id}">Отменить</button></div>
          </div>
        `).join("");

        qsa("[data-cancel-meeting]").forEach((btn) => {
          btn.addEventListener("click", async () => {
            if (!confirm("Отменить встречу?")) return;
            try {
              await api(`/meetings/${btn.dataset.cancelMeeting}`, { method: "DELETE" });
              showMessage("Встреча отменена");
              loadMeetings();
            } catch (err) {
              showMessage(err.message, "error");
            }
          });
        });
      } catch (err) {
        qs("#meetings-list").innerHTML = `<div class="error">${escapeHtml(err.message)}</div>`;
      }
    }

    qs("#meeting-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const rawIds = qs("#meeting-participant-ids").value.trim();
        const payload = {
          title: qs("#meeting-title").value.trim(),
          description: qs("#meeting-description").value.trim(),
          start_time: qs("#meeting-start").value,
          end_time: qs("#meeting-end").value,
          participant_ids: rawIds ? rawIds.split(",").map((v) => Number(v.trim())).filter(Boolean) : [],
        };
        await api("/meetings/", { method: "POST", body: JSON.stringify(payload) });
        showMessage("Встреча создана");
        e.target.reset();
        loadMeetings();
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    await loadMeetings();
  } catch {
    clearToken();
    window.location.href = "/";
  }
}

async function initEvaluationsPage() {
  ensureAuthPageAccess();
  renderSidebar("evaluations");
  attachLogout();
  try {
    const me = await loadMe();
    if (me.role !== "manager") qs("#create-evaluation-panel").classList.add("hidden");

    async function loadEvaluations() {
      try {
        const [items, average] = await Promise.all([
          api("/evaluations/my"),
          api("/evaluations/average"),
        ]);
        qs("#average-score").textContent = average.average_score ?? "—";
        qs("#evaluations-list").innerHTML = items.map((item) => `
          <div class="card">
            <div class="row">
              <div><h3>Задача #${escapeHtml(item.task_id)}</h3></div>
              <div><span class="badge">Оценка ${escapeHtml(item.score)}</span></div>
            </div>
            <div class="muted">Комментарий: ${escapeHtml(item.comment || "—")}</div>
            <div class="muted">Менеджер: ${escapeHtml(item.manager_id)} · Сотрудник: ${escapeHtml(item.employee_id)}</div>
            <div class="muted">Дата: ${fmtDate(item.created_at)}</div>
          </div>
        `).join("");
      } catch (err) {
        qs("#evaluations-list").innerHTML = `<div class="error">${escapeHtml(err.message)}</div>`;
      }
    }

    qs("#evaluation-form")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const payload = {
          task_id: Number(qs("#evaluation-task-id").value),
          score: Number(qs("#evaluation-score").value),
          comment: qs("#evaluation-comment").value.trim(),
        };
        await api("/evaluations/", { method: "POST", body: JSON.stringify(payload) });
        showMessage("Оценка добавлена");
        e.target.reset();
        loadEvaluations();
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    qs("#period-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const from = qs("#period-from").value;
        const to = qs("#period-to").value;
        const data = await api(`/evaluations/average-by-period?date_from=${encodeURIComponent(from)}&date_to=${encodeURIComponent(to)}`);
        qs("#period-average-result").textContent = data.average_score ?? "—";
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    await loadEvaluations();
  } catch {
    clearToken();
    window.location.href = "/";
  }
}

function buildMonthGrid(monthData) {
  const weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];
  const days = monthData.days || [];
  const map = new Map(days.map((d) => [Number(d.day), d.items || []]));
  const firstDate = new Date(monthData.year, monthData.month - 1, 1);
  const lastDate = new Date(monthData.year, monthData.month, 0);
  const jsFirstWeekday = firstDate.getDay();
  const offset = jsFirstWeekday === 0 ? 6 : jsFirstWeekday - 1;
  const totalCells = Math.ceil((offset + lastDate.getDate()) / 7) * 7;

  let html = `<table><thead><tr>${weekdays.map((d) => `<th>${d}</th>`).join("")}</tr></thead><tbody>`;
  for (let i = 0; i < totalCells; i += 7) {
    html += "<tr>";
    for (let j = 0; j < 7; j++) {
      const idx = i + j;
      const dayNumber = idx - offset + 1;
      if (dayNumber < 1 || dayNumber > lastDate.getDate()) {
        html += `<td class="calendar-cell"></td>`;
        continue;
      }
      const items = map.get(dayNumber) || [];
      html += `
        <td class="calendar-cell">
          <strong>${dayNumber}</strong>
          ${items.map((item) => `<div class="calendar-item">${escapeHtml(item.title || item.type || "Событие")}</div>`).join("")}
        </td>
      `;
    }
    html += "</tr>";
  }
  html += "</tbody></table>";
  return html;
}

async function initCalendarPage() {
  ensureAuthPageAccess();
  renderSidebar("calendar");
  attachLogout();
  try {
    await loadMe();

    qs("#month-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const year = qs("#calendar-year").value;
        const month = qs("#calendar-month").value;
        const data = await api(`/calendar/month?year=${year}&month=${month}`);
        qs("#month-table").innerHTML = buildMonthGrid(data);
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    qs("#day-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        const day = qs("#calendar-day").value;
        const data = await api(`/calendar/day?day=${day}`);
        qs("#day-items").innerHTML = `
          <div class="list">
            ${(data.items || []).length ? data.items.map((item) => `
              <div class="card">
                <h3>${escapeHtml(item.title || item.type || "Событие")}</h3>
                <div class="muted">Тип: ${escapeHtml(item.type || "—")}</div>
                <div class="muted">Время: ${escapeHtml(item.time || item.start_time || "—")}</div>
                <div class="muted">Описание: ${escapeHtml(item.description || "—")}</div>
              </div>
            `).join("") : `<div class="muted">На этот день событий нет</div>`}
          </div>
        `;
      } catch (err) {
        showMessage(err.message, "error");
      }
    });

    const now = new Date();
    qs("#calendar-year").value = now.getFullYear();
    qs("#calendar-month").value = now.getMonth() + 1;
    qs("#month-form").dispatchEvent(new Event("submit"));
  } catch {
    clearToken();
    window.location.href = "/";
  }
}

const page = document.body.dataset.page;
if (page === "auth") initAuthPage();
if (page === "dashboard") initDashboardPage();
if (page === "teams") initTeamsPage();
if (page === "tasks") initTasksPage();
if (page === "meetings") initMeetingsPage();
if (page === "evaluations") initEvaluationsPage();
if (page === "calendar") initCalendarPage();
