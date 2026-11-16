const form = document.getElementById("analyzer-form");
const followersInput = document.getElementById("followers-files");
const followingInput = document.getElementById("following-json");
const analyzeButton = document.getElementById("analyze-button");
const statusMessage = document.getElementById("status");
const results = document.getElementById("results");

const updateFileName = (input, nameElement) => {
  const files = Array.from(input.files);
  const emptyLabel = "Nenhum arquivo selecionado";
  nameElement.textContent = files.length > 1
    ? `${files.length} arquivos selecionados`
    : files[0]?.name || emptyLabel;
  input.closest(".upload-card").classList.toggle("is-selected", files.length > 0);
};

followersInput.addEventListener("change", () => {
  updateFileName(followersInput, document.getElementById("followers-name"));
});

followingInput.addEventListener("change", () => {
  updateFileName(followingInput, document.getElementById("following-name"));
});

const readFile = async (file) => {
  const content = await file.text();
  try {
    return JSON.parse(content);
  } catch {
    throw new Error(`O arquivo ${file.name} não contém um JSON válido.`);
  }
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

  const followerFiles = Array.from(followersInput.files);
  const followingFile = followingInput.files[0];
  if (followerFiles.length === 0 || !followingFile) {
    statusMessage.textContent = "Selecione os arquivos de seguidores e o arquivo following.json.";
    return;
  }

  analyzeButton.disabled = true;
  analyzeButton.querySelector("span").textContent = "Analisando...";
  statusMessage.textContent = "Lendo seus arquivos com segurança...";

  try {
    const body = JSON.stringify({
      followers_files: await Promise.all(followerFiles.map(readFile)),
      following: await readFile(followingFile),
    });
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
    const responseText = await response.text();
    let data;
    try {
      data = JSON.parse(responseText);
    } catch {
      if (!response.ok) {
        throw new Error(
          `O servidor não conseguiu processar a análise (HTTP ${response.status}). Confira se a API está ativa e tente novamente.`,
        );
      }
      throw new Error("O servidor retornou uma resposta inválida. Tente novamente.");
    }
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
