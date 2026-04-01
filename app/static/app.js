const state = {
  activeUser: null,
  games: [],
};

const USER_ATTRIBUTE_FIELDS = [
  "action_preference",
  "adventure_preference",
  "platformer_preference",
  "puzzle_horror_preference",
  "rpg_preference",
  "racing_preference",
  "shooter_preference",
  "simulation_preference",
  "sports_preference",
  "strategy_preference",
];

const elements = {
  openCreateUserModal: document.querySelector("#open-create-user-modal"),
  createUserModal: document.querySelector("#create-user-modal"),
  closeCreateUserModal: document.querySelector("#close-create-user-modal"),
  cancelCreateUser: document.querySelector("#cancel-create-user"),
  modalBackdrop: document.querySelector("#modal-backdrop"),
  createUserForm: document.querySelector("#create-user-form"),
  loadUserForm: document.querySelector("#load-user-form"),
  preferenceForm: document.querySelector("#preference-form"),
  recommendForm: document.querySelector("#recommend-form"),
  activeUser: document.querySelector("#active-user"),
  selectedGame: document.querySelector("#selected-game"),
  preferenceResult: document.querySelector("#preference-result"),
  recommendations: document.querySelector("#recommendations"),
  gameSelect: document.querySelector("#game-select"),
};

document.addEventListener("DOMContentLoaded", () => {
  setupEvents();
  loadGames();
});

function setupEvents() {
  elements.openCreateUserModal.addEventListener("click", openCreateUserModal);
  elements.closeCreateUserModal.addEventListener("click", closeCreateUserModal);
  elements.cancelCreateUser.addEventListener("click", closeCreateUserModal);
  elements.modalBackdrop.addEventListener("click", closeCreateUserModal);
  elements.createUserForm.addEventListener("submit", handleCreateUser);
  elements.loadUserForm.addEventListener("submit", handleLoadUser);
  elements.preferenceForm.addEventListener("submit", handleCreatePreference);
  elements.recommendForm.addEventListener("submit", handleGetRecommendations);
  elements.gameSelect.addEventListener("change", handleGameSelection);
  document.addEventListener("keydown", handleGlobalKeydown);
}

async function loadGames() {
  try {
    const response = await fetch("/game");
    const data = await response.json();
    state.games = data.games || [];
    renderGameOptions();
  } catch (error) {
    elements.gameSelect.innerHTML = "<option value=''>No se pudieron cargar los juegos</option>";
    showMessage(elements.selectedGame, "warning", getErrorMessage(error));
  }
}

function renderGameOptions() {
  if (!state.games.length) {
    elements.gameSelect.innerHTML = "<option value=''>No hay juegos disponibles</option>";
    return;
  }

  const options = ["<option value=''>Seleccioná un juego</option>"];
  for (const game of state.games) {
    options.push(`<option value="${game.id}">${escapeHtml(game.title)}</option>`);
  }
  elements.gameSelect.innerHTML = options.join("");
}

function handleGameSelection() {
  const selectedGame = getSelectedGame();
  if (!selectedGame) {
    showMessage(elements.selectedGame, "muted", "Elegí un juego para ver su detalle.");
    return;
  }

  elements.selectedGame.innerHTML = `
    <span class="status">Juego seleccionado</span>
    <strong>${escapeHtml(selectedGame.title)}</strong>
    <p class="meta">Géneros: ${escapeHtml(selectedGame.genres.join(", ") || "Sin datos")} | Userscore: ${selectedGame.userscore}</p>
    <p class="description">${escapeHtml(selectedGame.description || "Sin descripción disponible.")}</p>
  `;
}

async function handleCreateUser(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const username = String(formData.get("username") || "").trim();
  const attributes = buildUserAttributes(formData);

  if (!username) {
    showMessage(elements.activeUser, "warning", "Ingresá un nombre para crear el usuario.");
    return;
  }

  try {
    const response = await fetch("/user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, attributes }),
    });
    const data = await readJson(response);
    setActiveUser(data);
    form.reset();
    closeCreateUserModal();
    showMessage(elements.preferenceResult, "muted", "Usuario creado. Ya podés registrar una preferencia.");
  } catch (error) {
    showMessage(elements.activeUser, "warning", getErrorMessage(error));
  }
}

async function handleLoadUser(event) {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const userId = Number(formData.get("userId"));

  if (!userId) {
    showMessage(elements.activeUser, "warning", "Ingresá un ID de usuario válido.");
    return;
  }

  try {
    const response = await fetch(`/user/${userId}`);
    const data = await readJson(response);
    setActiveUser(data);
  } catch (error) {
    showMessage(elements.activeUser, "warning", getErrorMessage(error));
  }
}

async function handleCreatePreference(event) {
  event.preventDefault();

  if (!state.activeUser) {
    showMessage(elements.preferenceResult, "warning", "Primero seleccioná o creá un usuario.");
    return;
  }

  const formData = new FormData(event.currentTarget);
  const itemId = Number(formData.get("itemId"));
  const ranking = Number(formData.get("ranking"));
  const selectedGame = getSelectedGame();
  const previousAttributes = { ...(state.activeUser.attributes || {}) };

  if (!itemId || !ranking) {
    showMessage(elements.preferenceResult, "warning", "Elegí un juego y un ranking.");
    return;
  }

  try {
    const response = await fetch(`/user/${state.activeUser.id}/preference/${itemId}?ranking=${ranking}`, {
      method: "POST",
    });
    const data = await readJson(response);

    state.activeUser = {
      ...state.activeUser,
      attributes: data.updatedAttributes,
    };
    renderActiveUser();
    renderPreferenceResult(selectedGame, data.ranking, previousAttributes, data.updatedAttributes);
  } catch (error) {
    showMessage(elements.preferenceResult, "warning", getErrorMessage(error));
  }
}

async function handleGetRecommendations(event) {
  event.preventDefault();

  if (!state.activeUser) {
    showMessage(elements.recommendations, "warning", "Necesitás un usuario activo para pedir recomendaciones.");
    return;
  }

  const formData = new FormData(event.currentTarget);
  const count = Number(formData.get("count")) || 5;

  try {
    const response = await fetch(`/user/${state.activeUser.id}/recommend?n=${count}`);
    const data = await readJson(response);
    renderRecommendations(data.items || []);
  } catch (error) {
    showMessage(elements.recommendations, "warning", getErrorMessage(error));
  }
}

function setActiveUser(user) {
  state.activeUser = user;
  const userIdField = document.querySelector("#user-id");
  userIdField.value = user.id;
  renderActiveUser();
}

function renderActiveUser() {
  if (!state.activeUser) {
    showMessage(elements.activeUser, "muted", "Ningún usuario seleccionado.");
    return;
  }

  const attributes = Object.entries(state.activeUser.attributes || {});
  const attributesHtml = attributes.length
    ? attributes
        .map(([key, value]) => {
          const numericValue = Number(value);
          return `
            <li class="attribute-item ${getAttributeToneClass(numericValue)}">
              <strong>${formatLabel(key)}:</strong> ${numericValue.toFixed(2)}
            </li>
          `;
        })
        .join("")
    : "<li>Sin atributos disponibles</li>";

  elements.activeUser.innerHTML = `
    <span class="status">Usuario activo</span>
    <strong>${escapeHtml(state.activeUser.username)}</strong> <span>#${state.activeUser.id}</span>
    <p class="meta">Este bloque siempre muestra los atributos más recientes del usuario.</p>
    <ul class="attribute-list">${attributesHtml}</ul>
  `;
}

function renderRecommendations(items) {
  if (!items.length) {
    showMessage(elements.recommendations, "muted", "No llegaron recomendaciones para este usuario.");
    return;
  }

  elements.recommendations.className = "recommendations";
  elements.recommendations.innerHTML = items
    .map(
      (item) => `
        <article class="recommendation-card">
          <span class="status">Recomendación</span>
          <h3>${escapeHtml(item.name)}: ${renderGenreBadges(item.genre)}</h3>
          <p class="meta">ID: ${item.id} | Userscore: ${item.userscore}</p>
          <p class="description">${escapeHtml(item.description || "Sin descripción disponible.")}</p>
        </article>
      `
    )
    .join("");
}

function renderGenreBadges(genres) {
  const genreList = String(genres || "")
    .split(",")
    .map((genre) => genre.trim())
    .filter(Boolean);

  if (!genreList.length) {
    return `<span class="genre-badge">Sin datos</span>`;
  }

  return genreList
    .map((genre) => `<span class="genre-badge">${escapeHtml(genre)}</span>`)
    .join("");
}

function getSelectedGame() {
  const selectedId = Number(elements.gameSelect.value);
  return state.games.find((game) => game.id === selectedId);
}

function renderPreferenceResult(selectedGame, ranking, previousAttributes, updatedAttributes) {
  const gameName = selectedGame?.title || `Juego #${selectedGame?.id || ""}`.trim();
  const attributeChanges = getAttributeChanges(previousAttributes, updatedAttributes);

  const changesHtml = attributeChanges.length
    ? `
      <ul class="attribute-list attribute-changes">
        ${attributeChanges
          .map(
            ({ key, previousValue, nextValue, delta, tone }) => `
              <li>
                <strong>${escapeHtml(formatLabel(key))}:</strong>
                <span class="${tone}">${formatDelta(delta)}</span>
                <span class="change-values">(${previousValue.toFixed(2)} -> ${nextValue.toFixed(2)})</span>
              </li>
            `
          )
          .join("")}
      </ul>
    `
    : `<p class="meta">Esta preferencia no modificó atributos del perfil.</p>`;

  elements.preferenceResult.className = "result muted";
  elements.preferenceResult.innerHTML = `
    <span class="status">Preferencia registrada</span>
    <strong>${escapeHtml(gameName)}</strong>
    <p class="meta">Ranking enviado: ${ranking}</p>
    ${changesHtml}
  `;
}

function getAttributeChanges(previousAttributes, updatedAttributes) {
  const keys = Object.keys(updatedAttributes || {});

  return keys
    .map((key) => {
      const previousValue = Number(previousAttributes?.[key] || 0);
      const nextValue = Number(updatedAttributes?.[key] || 0);
      const delta = nextValue - previousValue;

      return {
        key,
        previousValue,
        nextValue,
        delta,
        tone: delta > 0 ? "positive" : delta < 0 ? "negative" : "muted",
      };
    })
    .filter(({ delta }) => Math.abs(delta) > 0.0001);
}

function buildUserAttributes(formData) {
  const attributes = {};

  for (const field of USER_ATTRIBUTE_FIELDS) {
    attributes[field] = Number(formData.get(field) || 0);
  }

  return attributes;
}

function openCreateUserModal() {
  elements.createUserModal.classList.remove("hidden");
  elements.createUserModal.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");
  document.querySelector("#modal-username")?.focus();
}

function closeCreateUserModal() {
  elements.createUserModal.classList.add("hidden");
  elements.createUserModal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open");
}

function handleGlobalKeydown(event) {
  if (event.key === "Escape" && !elements.createUserModal.classList.contains("hidden")) {
    closeCreateUserModal();
  }
}

function showMessage(target, type, message) {
  target.className = `result ${type}`;
  if (target === elements.recommendations) {
    target.className = `recommendations ${type}`;
  }
  target.textContent = message;
}

async function readJson(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || "La solicitud falló.");
  }
  return data;
}

function getErrorMessage(error) {
  return error instanceof Error ? error.message : "Ocurrió un error inesperado.";
}

function formatLabel(value) {
  const cleanedValue = value.replace("_preference", "").replaceAll("_", " ").trim();
  return cleanedValue.charAt(0).toUpperCase() + cleanedValue.slice(1);
}

function formatDelta(value) {
  if (value > 0) {
    return `+${value.toFixed(2)}`;
  }

  return value.toFixed(2);
}

function getAttributeToneClass(value) {
  if (value === 0) {
    return "attribute-zero";
  }

  if (value > 7) {
    return "attribute-high";
  }

  if (value > 3) {
    return "attribute-mid";
  }

  return "attribute-low";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
