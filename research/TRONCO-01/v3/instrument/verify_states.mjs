// Fase 1, segunda via independente (Node.js, sem código partilhado com o Python).
// Lê F1_ESTADOS.jsonl (estados em forma pública) e recalcula, só a partir do que o agente vê e da definição do espaço
// ("funções booleanas de 4 atributos binários com suporte essencial <= 2"), o veredicto nas duas leituras.
import fs from "node:fs";
import readline from "node:readline";

const FEATS = [["g0", "g1"], ["s0", "s1"], ["p0", "p1"], ["t0", "t1"]];
const INPUTS = [];
for (const a of FEATS[0]) for (const b of FEATS[1]) for (const c of FEATS[2]) for (const d of FEATS[3]) INPUTS.push([a, b, c, d]);
const idx = (x) => INPUTS.findIndex((y) => y.every((v, k) => v === x[k]));

// Every Boolean function on 16 inputs, kept if its essential support has at most 2 features.
function support(f) {
  let s = 0;
  for (let k = 0; k < 4; k++) {
    for (let i = 0; i < 16; i++) {
      const flipped = INPUTS[i].slice();
      flipped[k] = FEATS[k][1 - FEATS[k].indexOf(flipped[k])];
      if (((f >> i) & 1) !== ((f >> idx(flipped)) & 1)) { s++; break; }
    }
  }
  return s;
}
const SPACE = [];
for (let f = 0; f < 1 << 16; f++) if (support(f) <= 2) SPACE.push(f);

function decodeCard(table) {
  // Which features the keys use: a token belongs to feature k if it is one of FEATS[k].
  let f = 0;
  for (let i = 0; i < 16; i++) {
    const hit = Object.entries(table).filter(([key]) => key.split("|").every((tok) => INPUTS[i].includes(tok)));
    if (hit.length !== 1) throw new Error("card key does not resolve uniquely");
    if (hit[0][1] === "1") f |= 1 << i;
  }
  return f;
}

function verdict(A, W, T) {
  if (A.length === 0) return "inconsistent";
  if (!A.includes(W)) return "rejected";
  return A.every((h) => T.every((t) => ((h >> t) & 1) === ((W >> t) & 1))) ? "supported" : "undetermined";
}

const rl = readline.createInterface({ input: fs.createReadStream(process.argv[2]) });
let n = 0, bad70 = 0, badCards = 0;
for await (const line of rl) {
  if (!line) continue;
  const s = JSON.parse(line);
  const rows = s.node.rows.map(([x, y]) => [idx(x), y === "1" ? 1 : 0]);
  const fits = (h) => rows.every(([i, y]) => ((h >> i) & 1) === y);
  const W = decodeCard(s.node.working);
  const T = s.node.held_out.map(idx);
  const v70 = verdict(SPACE.filter(fits), W, T);
  const vc = verdict(s.node.cards.map(decodeCard).filter(fits), W, T);
  n++; if (v70 !== s.v70) bad70++; if (vc !== s.vcards) badCards++;
}
console.log(JSON.stringify({ space_size: SPACE.length, states: n, divergences_v70: bad70, divergences_cards: badCards }));
