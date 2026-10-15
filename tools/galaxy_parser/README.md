# Bundled Galaxy syntax parser

These four JavaScript files come from Talv's `plaxtony` npm package, version 1.10.5,
under its MIT license. They are unchanged except that generated source-map footer
comments may refer to files that are not bundled here.

- Upstream: https://github.com/Talv/plaxtony
- Package: https://www.npmjs.com/package/plaxtony/v/1.10.5
- Files: `lib/src/compiler/{parser,scanner,types,utils}.js`

Only the dependency-free parser is included. This checks Galaxy grammar, including
the position of array dimensions. It does not resolve SC2 dependencies, type-check
native API calls, or simulate gameplay. The Editor's compiler and Test Document
are still required for those checks.
