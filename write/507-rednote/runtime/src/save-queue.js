export function enqueueSave(previous, task) {
  return previous.catch(() => undefined).then(task)
}
