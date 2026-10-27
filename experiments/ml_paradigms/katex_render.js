// Read a JSON list of {tex, display} from stdin and write the KaTeX HTML for each to stdout (JSON list).
const katex = require('katex');
let buf = '';
process.stdin.on('data', (d) => { buf += d; });
process.stdin.on('end', () => {
  const items = JSON.parse(buf);
  const out = items.map((it) => katex.renderToString(it.tex, { displayMode: !!it.display, output: 'html', throwOnError: true, strict: 'ignore' }));
  process.stdout.write(JSON.stringify(out));
});
