function encodePathSegment(segment) {
  try {
    return encodeURIComponent(decodeURIComponent(segment))
  } catch {
    return encodeURIComponent(segment)
  }
}

export function projectAssetUrl(value, search = globalThis.location?.search || '') {
  if (!value || value.startsWith('data:') || value.startsWith('/project/')) return value
  if (/^https?:\/\//i.test(value)) return ''
  const clean = value.replace(/^\.\//, '').split('/').filter(Boolean).map(encodePathSegment).join('/')
  const token = new URLSearchParams(search).get('token') || ''
  return `/project/${clean}?token=${encodeURIComponent(token)}`
}
