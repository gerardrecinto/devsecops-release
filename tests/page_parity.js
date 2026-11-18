// Runs the page's triage() on every fixture log and prints the layers as JSON.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const dir = process.argv[3];
const code = html.match(/const TRIAGE=[\s\S]*?\n<\/script>/)[0].replace(/\n<\/script>$/, "");
const triage = new Function(code + "; return triage;")();
const out = {};
for (const f of fs.readdirSync(dir).filter(f => f.endsWith(".log"))) {
  const r = triage(fs.readFileSync(dir + "/" + f, "utf8"));
  out[f] = [r.layer, r.also];
}
console.log(JSON.stringify(out));
