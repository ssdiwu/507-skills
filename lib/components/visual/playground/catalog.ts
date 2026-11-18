import catalog from '../catalog.json'
export const examples = catalog.examples
export const groups = [...new Set(examples.map(e => e.group))]
