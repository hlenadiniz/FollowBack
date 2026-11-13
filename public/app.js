const readJson = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try { resolve(JSON.parse(reader.result)); } catch (e) { reject(e); }
    };
    reader.onerror = reject;
    reader.readAsText(file);
  });

document.getElementById("analyze").addEventListener("click", async () => {
  const status = document.getElementById("status");
  const list = document.getElementById("result");
  list.innerHTML = "";
  const f1 = document.getElementById("followers").files[0];
  const f2 = document.getElementById("following").files[0];
  if (!f1 || !f2) { status.textContent = "Selecione os dois arquivos."; return; }
  try {
    const body = JSON.stringify({ followers: await readJson(f1), following: await readJson(f2) });
    const res = await fetch("/api/analyze", { method: "POST", body });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);
    status.textContent = `${data.not_following_back.length} pessoas não te seguem de volta:`;
    data.not_following_back.forEach((u) => {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = `https://www.instagram.com/${u}`;
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = u;
      li.appendChild(a);
      list.appendChild(li);
    });
  } catch (e) {
    status.textContent = "Erro: arquivos inválidos.";
  }
});
