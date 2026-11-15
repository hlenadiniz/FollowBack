const form = document.getElementById("analyzer-form");
const followersInput = document.getElementById("followers-file");
const followingInput = document.getElementById("following-file");
const analyzeButton = document.getElementById("analyze-button");
const statusMessage = document.getElementById("status");
const results = document.getElementById("results");

const updateFileName = (input, nameElement) => {
  const file = input.files[0];
  nameElement.textContent = file ? file.name : "Escolher arquivo CSV ou JSON";
  input.closest(".upload-card").classList.toggle("is-selected", Boolean(file));
};

followersInput.addEventListener("change", () => {
  updateFileName(followersInput, document.getElementById("followers-name"));
});

followingInput.addEventListener("change", () => {
  updateFileName(followingInput, document.getElementById("following-name"));
});

const readFile = async (file) => {
  const content = await file.text();
  if (file.name.toLowerCase().endsWith(".json")) {
    try {
      return JSON.parse(content);
    } catch {
      throw new Error(`O arquivo ${file.name} não contém um JSON válido.`);
    }
  }
  return content;
};

const renderUserList = (elementId, users, emptyMessage) => {
  const list = document.getElementById(elementId);
  list.replaceChildren();
  if (users.length === 0) {
    const item = document.createElement("li");
    item.className = "empty-state";
    item.textContent = emptyMessage;
    list.appendChild(item);
    return;
  }

  users.forEach((username) => {
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = `https://www.instagram.com/${encodeURIComponent(username)}/`;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = `@${username}`;
    item.appendChild(link);
    list.appendChild(item);
  });
};

const renderResults = (data) => {
  const sections = [
    {
      key: "not_following_back",
      countId: "not-following-count",
      listCountId: "not-following-list-count",
      listId: "not-following-list",
      emptyMessage: "Boa! Todo mundo segue você de volta.",
    },
    {
      key: "mutuals",
      countId: "mutuals-count",
      listCountId: "mutuals-list-count",
      listId: "mutuals-list",
      emptyMessage: "Nenhuma conexão mútua nesta análise.",
    },
    {
      key: "fans",
      countId: "fans-count",
      listCountId: "fans-list-count",
      listId: "fans-list",
      emptyMessage: "Ninguém novo por aqui.",
    },
  ];

  sections.forEach(({ key, countId, listCountId, listId, emptyMessage }) => {
    const usernames = data[key];
    if (!Array.isArray(usernames)) {
      throw new Error("A resposta da análise veio em um formato inesperado.");
    }
    document.getElementById(countId).textContent = usernames.length;
    document.getElementById(listCountId).textContent = usernames.length;
    renderUserList(listId, usernames, emptyMessage);
  });

  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  results.hidden = true;
  statusMessage.classList.remove("is-error");

  const followersFile = followersInput.files[0];
  const followingFile = followingInput.files[0];
  if (!followersFile || !followingFile) {
    statusMessage.textContent = "Selecione os dois arquivos para continuar.";
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.querySelector("span").textContent = "Analisando...";
  statusMessage.textContent = "Lendo seus arquivos com segurança...";

  try {
    const body = JSON.stringify({
      followers: await readFile(followersFile),
      following: await readFile(followingFile),
    });
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Não foi possível analisar os arquivos.");
    }

    renderResults(data);
    const count = data.not_following_back.length;
    statusMessage.textContent = count
      ? `Análise pronta: ${count} ${count === 1 ? "perfil não segue" : "perfis não seguem"} você de volta.`
      : "Análise pronta: todos os perfis que você segue também seguem você.";
  } catch (error) {
    statusMessage.textContent = error.message || "Não foi possível ler os arquivos selecionados.";
    statusMessage.classList.add("is-error");
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.querySelector("span").textContent = "Analisar meus arquivos";
  }
});

document.getElementById("reset-button").addEventListener("click", () => {
  form.reset();
  updateFileName(followersInput, document.getElementById("followers-name"));
  updateFileName(followingInput, document.getElementById("following-name"));
  results.hidden = true;
  statusMessage.textContent = "";
  statusMessage.classList.remove("is-error");
  followersInput.focus();
});
