// Syntax checking only. SC2 Editor remains the authority for type and runtime checks.
const fs = require('node:fs');
const { Parser } = require('./galaxy_parser/parser.js');

function diagnostics(file, source) {
    return new Parser().parseFile(file, source).parseDiagnostics.map(d => ({
        file,
        line: d.line + 1,
        column: d.col + 1,
        message: d.messageText,
    }));
}

if (process.argv.includes('--self-test')) {
    const bad = diagnostics('bad.galaxy', 'int buttons[3];');
    const good = diagnostics('good.galaxy', 'int[3] buttons;');
    if (bad.length === 0 || good.length !== 0) {
        throw new Error('Galaxy array syntax regression test failed.');
    }
    console.log('PASS: C-style array declaration rejected; Galaxy array declaration accepted.');
} else {
    const files = process.argv.slice(2);
    if (!files.length) throw new Error('Pass at least one Galaxy script path.');
    const errors = files.flatMap(file => diagnostics(file, fs.readFileSync(file, 'utf8')));
    for (const d of errors) console.error(`${d.file}:${d.line}:${d.column}: ${d.message}`);
    if (errors.length) {
        process.exitCode = 1;
    } else {
        console.log(`PASS: Galaxy syntax checked for ${files.length} file(s).`);
    }
}
