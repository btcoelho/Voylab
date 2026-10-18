// Fase 3: verificação independente das respostas certas a partir do TEXTO apresentado ao modelo (system + user).
// Não usa nada do Python: lê os atributos do system prompt, as observações, as cartas, W e as retidas do texto.
import fs from "node:fs";

function parse(item) {
  const m = item.system.match(/quatro atributos \(([^)]+)\)/);
  const feats = m[1].split(",").map((s) => s.trim());
  const lines = item.user.split("\n");
  const inputOf = (txt) => {
    const d = Object.fromEntries(txt.split(",").map((kv) => kv.trim().split("=")));
    return feats.map((f) => d[f]);
  };
  const st = { obs: [], newEv: [], cards: {}, W: null, T: [], menu: {} };
  let sec = null, cur = null;
  for (const l of lines) {
    if (/^OBSERVAÇÕES/.test(l)) { sec = "obs"; continue; }
    if (/^EVIDÊNCIA NOVA/.test(l)) { sec = "new"; continue; }
    if (/^CARTAS/.test(l)) { sec = "cards"; continue; }
    if (/^CARTA DE TRABALHO: /.test(l)) { st.W = l.split(": ")[1].trim(); sec = null; continue; }
    if (/^ENTRADAS RETIDAS/.test(l)) { sec = "T"; continue; }
    if (/^CONSULTAS DISPONÍVEIS/.test(l)) { sec = "menu"; continue; }
    if (/^(AÇÕES|PERGUNTA)/.test(l)) { sec = null; continue; }
    if (sec === "obs" || sec === "new") {
      const mm = l.match(/^- (\S+): (.*) -> ([01])$/);
      if (mm) (sec === "obs" ? st.obs : st.newEv).push([inputOf(mm[2]), mm[3]]);
    } else if (sec === "cards") {
      const head = l.match(/^- (\S+) \(/);
      if (head) { cur = head[1]; st.cards[cur] = {}; continue; }
      const row = l.match(/^\s+(\S+) -> ([01])$/);
      if (row) st.cards[cur][row[1]] = row[2];
    } else if (sec === "T") {
      const mm = l.match(/^- \d+: (.*)$/);
      if (mm) st.T.push(inputOf(mm[1]));
    } else if (sec === "menu") {
      const mm = l.match(/^- (q\d+): (.*)$/);
      if (mm) st.menu[mm[1]] = inputOf(mm[2]);
    }
  }
  return { feats, st };
}

// Space: all Boolean functions of the 4 attributes (values read from the text) with essential support <= 2.
function universe(st) {
  const vals = [0, 1, 2, 3].map(() => new Set());
  const add = (x) => x.forEach((v, k) => vals[k].add(v));
  st.obs.forEach(([x]) => add(x)); st.newEv.forEach(([x]) => add(x)); st.T.forEach(add); Object.values(st.menu).forEach(add);
  const V = vals.map((s) => [...s].sort());
  if (V.some((v) => v.length !== 2)) throw new Error("could not read both values of every attribute");
  const inputs = [];
  for (const a of V[0]) for (const b of V[1]) for (const c of V[2]) for (const d of V[3]) inputs.push([a, b, c, d]);
  const key = (x) => x.join(",");
  const pos = Object.fromEntries(inputs.map((x, i) => [key(x), i]));
  const space = [];
  for (let f = 0; f < 1 << 16; f++) {
    let s = 0;
    for (let k = 0; k < 4; k++) {
      for (let i = 0; i < 16; i++) {
        const y = inputs[i].slice(); y[k] = V[k][1 - V[k].indexOf(y[k])];
        if (((f >> i) & 1) !== ((f >> pos[key(y)]) & 1)) { s++; break; }
      }
    }
    if (s <= 2) space.push(f);
  }
  return { inputs, pos, key, space };
}

function cardFn(table, U) {
  let f = 0;
  U.inputs.forEach((x, i) => {
    const hit = Object.entries(table).filter(([k]) => k.split("|").every((t) => x.includes(t)));
    if (hit.length !== 1) throw new Error("card key does not resolve");
    if (hit[0][1] === "1") f |= 1 << i;
  });
  return f;
}

function verdict(A, W, T) {
  if (!A.length) return "inconsistent";
  if (!A.includes(W)) return "rejected";
  return A.every((h) => T.every((t) => ((h >> t) & 1) === ((W >> t) & 1))) ? "supported" : "undetermined";
}

let n = 0, bad = 0, checked = {};
const lines = fs.readFileSync(process.argv[2], "utf8").split("\n").filter(Boolean);
for (const line of lines) {
  const it = JSON.parse(line);
  if (it.family === "query_choice") continue;
  const { st } = parse(it);
  const U = universe(st);
  const rows = st.obs.map(([x, y]) => [U.pos[U.key(x)], +y]);
  const fits = (h) => rows.every(([i, y]) => ((h >> i) & 1) === y);
  const cards = Object.fromEntries(Object.entries(st.cards).map(([k, t]) => [k, cardFn(t, U)]));
  const T = st.T.map((x) => U.pos[U.key(x)]);
  let got;
  const q = (it.user.split("PERGUNTA: ")[1] || "");
  if (it.family === "par_minimo" || it.family === "meta_verdict") {
    got = verdict(U.space.filter(fits), cards[st.W], T) + '"';
  } else if (it.family === "sonda_celula") {
    const mm = q.match(/carta (\S+), qual é a saída para a entrada (.*)\? Responde/);
    const d = Object.fromEntries(mm[2].split(",").map((kv) => kv.trim().split("=")));
    const x = parse(it).feats.map((f) => d[f]);
    got = String((cards[mm[1]] >> U.pos[U.key(x)]) & 1);
  } else if (it.family === "sonda_compat") {
    const c = q.match(/A carta (\S+) reproduz/)[1];
    got = fits(cards[c]) ? "sim" : "não";
  } else if (it.family === "sonda_separa") {
    const mm = q.match(/consulta (q\d+) .* as cartas (\S+) e (\S+) dão/);
    const i = U.pos[U.key(st.menu[mm[1]])];
    got = ((cards[mm[2]] >> i) & 1) !== ((cards[mm[3]] >> i) & 1) ? "sim" : "não";
  } else if (it.family === "sonda_veredicto") {
    // Answer from the stated information only, then cross-check the stated information against the state.
    const win = /W É admissível/.test(q);
    const pats = q.match(/padrões de saída: ([01, ]+)\./)[1].split(",").map((s) => s.trim());
    const wpat = q.match(/W dá o padrão ([01]+)/)[1];
    got = !win ? "rejected" : pats.every((p) => p === wpat) ? "supported" : "undetermined";
    const A = U.space.filter(fits);
    const truePats = [...new Set(A.map((h) => T.map((t) => (h >> t) & 1).join("")))].sort();
    if (A.includes(cards[st.W]) !== win || truePats.join() !== pats.join()) got = "INFO_ERRADA";
  } else if (it.family === "sonda_contradicao") {
    const seen = Object.fromEntries(st.obs.map(([x, y]) => [U.key(x), y]));
    got = st.newEv.some(([x, y]) => seen[U.key(x)] !== undefined && seen[U.key(x)] !== y) ? "sim" : "não";
  }
  n++; checked[it.family] = (checked[it.family] || 0) + 1;
  if (got !== it.answer) { bad++; if (bad < 5) console.error("DIF", it.item_id, got, it.answer); }
}
console.log(JSON.stringify({ items_checked: n, by_family: checked, divergences: bad }));
