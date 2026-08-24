import {createHash} from 'node:crypto'
import {readdir, readFile, writeFile} from 'node:fs/promises'
import {join, relative} from 'node:path'
import {build} from 'esbuild'

const root = new URL('.', import.meta.url).pathname
const normalize = value => value.split('/').join('/')
const sha256 = buffer => createHash('sha256').update(buffer).digest('hex')

async function sourceFiles(directory) {
  const entries = await readdir(directory, {withFileTypes: true})
  const result = []
  for (const entry of entries) {
    const path = join(directory, entry.name)
    if (entry.isDirectory()) result.push(...await sourceFiles(path))
    else if (entry.isFile()) result.push(path)
  }
  return result
}

await build({
  entryPoints: [join(root, 'src/app.js')],
  bundle: true,
  minify: true,
  outfile: join(root, 'dist/app.js'),
})

const declaredInputs = [
  join(root, 'index.html'),
  join(root, 'styles.css'),
  join(root, 'package.json'),
  join(root, 'package-lock.json'),
  ...await sourceFiles(join(root, 'fonts')),
  ...await sourceFiles(join(root, 'src')),
].sort()
const inputs = []
for (const path of declaredInputs) {
  const content = await readFile(path)
  inputs.push({path: normalize(relative(root, path)), sha256: sha256(content)})
}
const bundle = await readFile(join(root, 'dist/app.js'))
const manifest = {
  schemaVersion: 1,
  inputs,
  bundle: {path: 'dist/app.js', sha256: sha256(bundle), bytes: bundle.length},
}
await writeFile(join(root, 'dist/build-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`)
