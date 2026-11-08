const app = document.querySelector("#app");
const userbar = document.querySelector("#userbar");
let currentUser = null;
let csrfToken = "";
let dashboardData = null;

const roleName = { instructor: "Instrutor", evaluator: "Avaliador", student: "Aluno" };
const statusName = {
  draft: "Em elaboração", submitted: "Aguardando avaliador", returned: "Em revisão",
  validated: "Aguardando instrutor", released: "Resultado liberado"
};
const deadlineName = { no_deadline: "Sem prazo configurado", needs_timezone: "Prazo anterior sem fuso: o instrutor deve salvá-lo novamente", within_deadline: "Dentro do prazo", overdue: "Entrega pendente após o prazo", submitted_late: "Versão entregue após o prazo", submitted_on_time: "Versão entregue dentro do prazo" };
function localInputDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,"0")}-${String(date.getDate()).padStart(2,"0")}T${String(date.getHours()).padStart(2,"0")}:${String(date.getMinutes()).padStart(2,"0")}`;
}

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key.startsWith("on") && typeof value === "function") node.addEventListener(key.slice(2).toLowerCase(), value);
    else if (value !== null && value !== undefined) node.setAttribute(key, value);
  }
  for (const child of children) if (child) node.append(child);
  return node;
}

async function api(path, body) {
  const headers = { "Content-Type": "application/json" };
  if (csrfToken) headers["X-CSRF-Token"] = csrfToken;
  const response = await fetch(path, {
    method: body === undefined ? "GET" : "POST",
    headers,
    credentials: "same-origin",
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok && !data.confirmation_required) throw new Error(data.error || "Não foi possível concluir a solicitação.");
  return data;
}

function showMessage(parent, text, kind = "notice") {
  const box = el("div", { class: kind, role: kind === "notice error" ? "alert" : "status", text });
  parent.prepend(box);
  window.setTimeout(() => box.remove(), 7000);
}

function renderLogin(message = "") {
  currentUser = null;
  userbar.hidden = true;
  app.replaceChildren();
  const form = el("form", { class: "card form-narrow" });
  form.append(el("h1", { class: "page-heading", text: "Acessar exercício" }));
  form.append(el("p", { class: "lede", text: "Entre com uma conta demonstrativa atribuída ao exercício." }));
  const usernameLabel = el("label", { class: "label", for: "username", text: "Usuário" });
  const username = el("input", { id: "username", name: "username", autocomplete: "username", required: "required" });
  const passwordLabel = el("label", { class: "label", for: "password", text: "Senha" });
  const password = el("input", { id: "password", name: "password", type: "password", autocomplete: "current-password", required: "required" });
  const submit = el("button", { class: "btn", type: "submit", text: "Entrar" });
  form.append(usernameLabel, username, passwordLabel, password, el("div", { class: "actions" }, [submit]));
  form.append(el("p", { class: "muted", text: "Somente demonstração local; os dados deste exercício são sintéticos." }));
  if (message) showMessage(form, message, "notice error");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    submit.disabled = true;
    try {
      await api("/api/login", { username: username.value.trim(), password: password.value });
      await loadDashboard();
    } catch (error) {
      showMessage(form, error.message, "notice error");
    } finally {
      submit.disabled = false;
    }
  });
  app.append(form);
}

function updateUserbar(user) {
  userbar.hidden = false;
  userbar.replaceChildren(
    el("span", { text: `${user.name} · ${roleName[user.role]}${user.team ? ` ${user.team}` : ""}` }),
    el("button", { type: "button", text: "Sair", onclick: async () => {
      try { await api("/api/logout", {}); } catch (_) { /* Cookie expirará localmente. */ }
      csrfToken = "";
      renderLogin();
    } })
  );
}

async function loadDashboard() {
  try {
    dashboardData = await api("/api/dashboard");
    currentUser = dashboardData.user;
    csrfToken = dashboardData.csrf;
    updateUserbar(currentUser);
    renderDashboard();
  } catch (error) {
    csrfToken = "";
    renderLogin(error.message);
  }
}

function renderDashboard() {
  if (!dashboardData || !currentUser) return renderLogin();
  app.replaceChildren();
  const exercise = dashboardData.exercise;
  if (!exercise) {
    app.append(el("div", { class: "card empty", text: dashboardData.error || "Nenhum exercício atribuído." }));
    return;
  }
  app.append(el("h1", { class: "page-heading", text: exercise.title }));
  app.append(el("p", { class: "lede", text: exercise.objective }));
  if (currentUser.role === "student") app.append(el("p", { class: "notice", text: `${deadlineName[dashboardData.deadline_status] || ""}${exercise.due_at ? ` · Prazo: ${new Date(exercise.due_at).toLocaleString("pt-BR")}` : ""}. A indicação considera a versão mais recente e o prazo atual; não aplica penalização automática.` }));
  app.append(el("div", { class: "notice warning", text: "Exercício didático sintético. Não contém dados operacionais nem recomendações de emprego." }));
  if (dashboardData.error) {
    app.append(el("div", { class: "card empty", text: dashboardData.error }));
    return;
  }
  if (currentUser.role === "student") renderStudent();
  else renderReviewer();
}

function renderStudent() {
  const box = el("section", { class: "grid" });
  const formCard = el("div", { class: "card span-7" });
  formCard.append(el("h2", { text: "Compor grupamento e registrar documento" }));
  formCard.append(el("p", { class: "muted", text: "Selecione apenas os meios sintéticos disponibilizados para sua equipe. A seleção não altera o cadastro do exercício." }));

  const form = el("form");
  const type = el("select", { id: "document-type", name: "document_type" });
  for (const value of ["Exame da Situação", "EPO"]) type.append(el("option", { value, text: value }));
  const group = el("input", { id: "group-name", name: "group_name", maxlength: "100", required: "required", value: "Grupamento 1" });
  const assets = el("div", { class: "asset-list" });
  for (const asset of dashboardData.assets || []) {
    const check = el("input", { type: "checkbox", name: "asset", value: String(asset.id), id: `asset-${asset.id}` });
    const text = el("span", {}, [el("strong", { text: `${asset.name} · ${asset.category}` }), el("small", { text: `${asset.code} — ${asset.source_label}. ${asset.fiche}` })]);
    assets.append(el("label", { class: "asset", for: `asset-${asset.id}` }, [check, text]));
  }
  const rationale = el("textarea", { id: "rationale", name: "rationale", maxlength: "12000", placeholder: "Justificativa facultativa. Se enviada vazia, será exibido o aviso aprovado e a ausência ficará registrada." });
  const save = el("button", { class: "btn btn-secondary", type: "button", text: "Salvar rascunho" });
  const submit = el("button", { class: "btn", type: "button", text: "Submeter ao avaliador" });
  const latest = (dashboardData.submissions || [])[0];
  const editable = !latest || ["draft", "returned"].includes(latest.status);
  if (latest) {
    type.value = latest.document_type;
    group.value = latest.group_name;
    rationale.value = latest.rationale;
    for (const check of assets.querySelectorAll('input[name="asset"]')) {
      check.checked = latest.asset_ids.includes(Number(check.value));
    }
  }
  if (!editable) {
    for (const input of [type, group, rationale, ...assets.querySelectorAll("input"), save, submit]) input.disabled = true;
    formCard.append(el("p", { class: "notice", text: "Documento submetido. O conteúdo permanece disponível para consulta; uma nova versão poderá ser preparada após devolução para revisão." }));
  } else if (latest) {
    formCard.append(el("p", { class: "notice", text: latest.status === "draft" ? `Rascunho da versão ${latest.revision} recuperado.` : `Conteúdo devolvido da versão ${latest.revision} recuperado. Ao salvar, será criada uma nova versão.` }));
  }
  form.append(el("label", { class: "label", for: "document-type", text: "Documento" }), type,
    el("label", { class: "label", for: "group-name", text: "Nome do grupamento" }), group,
    el("span", { class: "label", text: "Meios didáticos disponíveis" }), assets,
    el("label", { class: "label", for: "rationale", text: "Justificativa (facultativa)" }), rationale,
    el("div", { class: "actions" }, [save, submit]));
  const submitForm = async (doSubmit) => {
    save.disabled = submit.disabled = true;
    const payload = {
      document_type: type.value,
      group_name: group.value,
      asset_ids: [...form.querySelectorAll('input[name="asset"]:checked')].map((input) => Number(input.value)),
      rationale: rationale.value,
      submit: doSubmit
    };
    try {
      let result = await api("/api/submission", payload);
      if (result.confirmation_required) {
        if (!window.confirm(result.warning)) return;
        payload.confirm_no_rationale = true;
        result = await api("/api/submission", payload);
      }
      showMessage(formCard, doSubmit ? `Documento submetido. Versão ${result.revision} registrada.` : "Rascunho salvo.", "notice success");
      await loadDashboard();
    } catch (error) {
      showMessage(formCard, error.message, "notice error");
    } finally {
      save.disabled = submit.disabled = false;
    }
  };
  save.addEventListener("click", () => submitForm(false));
  submit.addEventListener("click", () => submitForm(true));
  formCard.append(form);

  const historyCard = el("div", { class: "card span-5" });
  historyCard.append(el("h2", { text: "Minhas versões" }));
  if (!(dashboardData.submissions || []).length) historyCard.append(el("div", { class: "empty", text: "Nenhum documento salvo." }));
  for (const item of dashboardData.submissions || []) {
    const shownStatus = item.status === "validated" ? "Aguardando instrutor" : statusName[item.status];
    const entry = el("article", { class: "submission" });
    entry.append(el("div", { class: "submission-meta" }, [el("strong", { text: `${item.document_type} · versão ${item.revision}` }),
      el("span", { class: `badge status-${item.status}`, text: shownStatus })]));
    entry.append(el("p", { class: "muted", text: `Grupamento: ${item.group_name} · registrada ${item.updated_at}` }));
    const content = el("details");
    const selectedNames = (dashboardData.assets || []).filter((asset) => item.asset_ids.includes(asset.id)).map((asset) => `${asset.code} — ${asset.name}`);
    content.append(el("summary", { text: "Consultar conteúdo desta versão" }),
      el("p", { text: `Meios: ${selectedNames.join("; ") || "nenhum selecionado"}` }),
      el("p", { text: item.rationale || "Justificativa não apresentada." }),
      el("p", { class: "muted", text: `Cenário de referência: versão ${item.scenario_version}` }));
    entry.append(content);
    if (item.status === "returned" || item.status === "released") {
      entry.append(el("p", { text: item.review_comment ? `Comentário: ${item.review_comment}` : "Sem comentário registrado." }));
    }
    historyCard.append(entry);
    if (item.status === "released") entry.append(el("a", { href: `/report/${item.id}`, target: "_blank", rel: "noopener", text: "Abrir relatório individual" }));
  }
  box.append(formCard, historyCard);
  const flowCard = el("section", { class: "card span-12" });
  flowCard.append(el("h2", { text: "Fluxograma de referência" }));
  flowCard.append(el("p", { class: "muted", text: "Consulte o fluxo confirmado pelo responsável. As respostas e avaliações permanecem humanas; o protótipo não automatiza as decisões do diagrama." }));
  const figure = el("figure", { class: "flow-figure" });
  figure.append(el("a", { href: "/fluxograma.jpg", target: "_blank", rel: "noopener noreferrer", "aria-label": "Abrir fluxograma em tamanho original" }, [
    el("img", { src: "/fluxograma.jpg", alt: "Fluxograma: Missão, Exame da Situação, EPO e Controle da Operação Planejada com decisões Sim e Não." })
  ]));
  flowCard.append(figure);
  box.append(flowCard);
  app.append(box);
}

function renderReviewer() {
  const box = el("div", { class: "grid" });
  if (currentUser.role === "instructor") {
    renderExerciseConfig(box);
    renderScenarioEditor(box);
    renderParticipants(box);
  }
  const list = el("section", { class: `card ${currentUser.role === "instructor" ? "span-12" : "span-12"}` });
  list.append(el("h2", { text: currentUser.role === "instructor" ? "Submissões do exercício" : "Documentos para avaliação" }));
  const items = dashboardData.submissions || [];
  if (!items.length) list.append(el("div", { class: "empty", text: "Ainda não há documentos submetidos." }));
  for (const item of items) list.append(renderSubmission(item));
  box.append(list);
  if (currentUser.role === "instructor") renderEventLog(box);
  app.append(box);
}

function renderScenarioEditor(parent) {
  const card = el("section", { class: "card span-12" });
  card.append(el("h2", { text: `Cenário · versão ${dashboardData.exercise.scenario_version}` }));
  card.append(el("p", { class: "muted", text: "Mudanças durante o exercício são permitidas. Antes de salvar, o aviso obrigatório será exibido. Cada alteração cria uma versão e registra autoria, horário e justificativa informada." }));
  const form = el("form");
  const title = el("input", { id: "scenario-title", maxlength: "160", required: "required", value: dashboardData.exercise.title });
  const objective = el("textarea", { id: "scenario-objective", maxlength: "4000", required: "required" });
  objective.value = dashboardData.exercise.objective;
  const note = el("textarea", { id: "scenario-note", maxlength: "1000", placeholder: "Justificativa da alteração (facultativa)" });
  const save = el("button", { class: "btn", type: "submit", text: "Salvar nova versão" });
  form.append(el("label", { class: "label", for: "scenario-title", text: "Título do cenário" }), title,
    el("label", { class: "label", for: "scenario-objective", text: "Objetivo" }), objective,
    el("label", { class: "label", for: "scenario-note", text: "Justificativa da alteração" }), note,
    el("div", { class: "actions" }, [save]));
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const payload = { title: title.value, objective: objective.value, change_note: note.value };
    try {
      let result = await api("/api/scenario", payload);
      if (result.confirmation_required) {
        if (!window.confirm(result.warning)) return;
        payload.confirm_change = true;
        result = await api("/api/scenario", payload);
      }
      showMessage(card, `Cenário atualizado. Versão ${result.scenario_version} registrada.`, "notice success");
      await loadDashboard();
    } catch (error) { showMessage(card, error.message, "notice error"); }
  });
  card.append(form);
  const history = el("div", { class: "scenario-history" });
  history.append(el("h3", { text: "Versões preservadas" }));
  for (const version of dashboardData.scenario_versions || []) {
    const label = version.changed_by || "Versão inicial";
    history.append(el("article", { class: "submission" }, [
      el("strong", { text: `v${version.version} · ${version.title}` }),
      el("p", { class: "muted", text: `${label} · ${version.changed_at}${version.change_note ? ` · Justificativa: ${version.change_note}` : ""}` }),
      el("p", { text: version.objective })
    ]));
  }
  card.append(history);
  parent.append(card);
}

function renderParticipants(parent) {
  const card = el("section", { class: "card span-12" });
  card.append(el("h2", { text: "Acompanhamento da turma" }));
  const participants = dashboardData.participants || [];
  const filter = el("select", { "aria-label": "Filtrar participantes por equipe" }, [
    el("option", { value: "", text: "Todas as equipes" }),
    el("option", { value: "AZUL", text: "Azul" }),
    el("option", { value: "VERMELHO", text: "Vermelho" })
  ]);
  const summary = el("p", { class: "muted", role: "status" });
  const list = el("div");
  const render = () => {
    const shown = participants.filter((item) => !filter.value || item.team === filter.value);
    summary.textContent = `${shown.length} participantes · ${shown.filter((item) => !item.status).length} não iniciaram · ${shown.filter((item) => item.status === "released").length} com resultado liberado`;
    list.replaceChildren();
    if (!shown.length) list.append(el("p", { class: "empty", text: "Nenhum participante nesta seleção." }));
    for (const item of shown) {
      list.append(el("article", { class: "submission" }, [
        el("strong", { text: `${item.display_name} · ${item.team}` }),
        el("span", { class: `badge status-${item.status || "not-started"}`, text: statusName[item.status] || "Não iniciado" }),
        el("p", { class: "muted", text: item.revision ? `${item.document_type} · versão ${item.revision} · última atualização ${item.updated_at}` : "Nenhum rascunho ou documento registrado." }),
        el("p", { text: deadlineName[item.deadline_status] || "" })
      ]));
    }
  };
  filter.addEventListener("change", render);
  card.append(filter, summary, list);
  render();
  parent.append(card);
}

function renderExerciseConfig(parent) {
  const card = el("section", { class: "card span-12" });
  card.append(el("h2", { text: "Configuração deste exercício" }));
  card.append(el("p", { class: "muted", text: "Prazos e tentativas são configurados por exercício. Deixar tentativas sem limite e prazo vazio é apenas a configuração demonstrativa atual." }));
  const form = el("form", { class: "grid" });
  const attempts = el("input", { type: "number", min: "1", max: "100", id: "max-attempts", value: dashboardData.exercise.max_attempts || "" });
  const due = el("input", { type: "datetime-local", id: "due-at", value: localInputDate(dashboardData.exercise.due_at) });
  const save = el("button", { class: "btn", type: "submit", text: "Salvar configuração" });
  form.append(el("div", { class: "span-6" }, [el("label", { class: "label", for: "max-attempts", text: "Tentativas máximas (vazio = sem limite)" }), attempts]),
    el("div", { class: "span-6" }, [el("label", { class: "label", for: "due-at", text: "Prazo (opcional)" }), due]),
    el("div", { class: "span-12 actions" }, [save]));
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api("/api/exercise-config", { max_attempts: attempts.value || null, due_at: due.value ? new Date(due.value).toISOString() : null });
      showMessage(card, "Configuração registrada no histórico.", "notice success");
      await loadDashboard();
    } catch (error) { showMessage(card, error.message, "notice error"); }
  });
  card.append(form);
  parent.append(card);
}

function renderSubmission(item) {
  const card = el("article", { class: "submission" });
  const label = `${item.student_name} · ${item.team} · ${item.document_type} · versão ${item.revision}`;
  card.append(el("div", { class: "submission-meta" }, [el("strong", { text: label }),
    el("span", { class: `badge status-${item.status}`, text: statusName[item.status] || item.status })]));
  card.append(el("p", { text: `Grupamento: ${item.group_name} · cenário v${item.scenario_version} · submetido ${item.submitted_at || "—"}` }));
  const selected = (dashboardData.assets || []).filter((asset) => item.asset_ids.includes(asset.id));
  card.append(el("p", { class: "muted", text: `Meios: ${selected.length ? selected.map((asset) => `${asset.name} (${asset.team})`).join(", ") : "nenhum selecionado"}` }));
  card.append(el("p", { text: item.rationale ? `Justificativa: ${item.rationale}` : "Justificativa ausente." }));
  if (item.review_comment) card.append(el("p", { class: "notice", text: `Comentário registrado: ${item.review_comment}` }));
  if (item.status === "submitted" || (currentUser.role === "instructor" && item.status === "validated")) {
    const form = el("form", { class: "review-form" });
    const comment = el("textarea", { maxlength: "8000", placeholder: "Comentário qualitativo do avaliador/instrutor (sem pontuação automática)." });
    const returnButton = el("button", { class: "btn btn-warn", type: "button", text: "Devolver para revisão" });
    const validateButton = item.status === "submitted"
      ? el("button", { class: "btn btn-positive", type: "button", text: "Validar documento" })
      : null;
    const act = async (status) => {
      try {
        await api("/api/review", { submission_id: item.id, status, comment: comment.value });
        await loadDashboard();
      } catch (error) { showMessage(card, error.message, "notice error"); }
    };
    returnButton.addEventListener("click", () => act("returned"));
    if (validateButton) validateButton.addEventListener("click", () => act("validated"));
    form.append(el("label", { class: "label", text: currentUser.role === "instructor" && item.status === "validated" ? "Comentário do instrutor" : "Comentário de avaliação" }), comment,
      el("div", { class: "actions" }, [returnButton, validateButton]));
    card.append(form);
  }
  if (currentUser.role === "instructor" && item.status === "validated") {
    const release = el("button", { class: "btn btn-positive", type: "button", text: "Liberar resultado ao aluno", onclick: async () => {
      try { await api("/api/release", { submission_id: item.id }); await loadDashboard(); }
      catch (error) { showMessage(card, error.message, "notice error"); }
    } });
    card.append(el("div", { class: "actions" }, [release]));
  }
  card.append(el("a", { href: `/report/${item.id}`, target: "_blank", rel: "noopener", text: "Abrir relatório individual" }));
  return card;
}

function renderEventLog(parent) {
  const card = el("section", { class: "card span-12" });
  card.append(el("h2", { text: "Histórico recente" }));
  const events = dashboardData.events || [];
  if (!events.length) card.append(el("div", { class: "empty", text: "Nenhuma ação registrada ainda." }));
  for (const item of events) {
    card.append(el("p", { class: "submission", text: `${item.created_at} · ${item.display_name} · ${item.event_type}` }));
  }
  parent.append(card);
}

async function start() {
  try {
    const response = await api("/api/me");
    if (!response.user) return renderLogin();
    csrfToken = response.csrf;
    currentUser = response.user;
    updateUserbar(currentUser);
    await loadDashboard();
  } catch (_) {
    renderLogin();
  }
}

start();
