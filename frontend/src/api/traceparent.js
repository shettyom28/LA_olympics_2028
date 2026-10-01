// W3C traceparent header generation (https://www.w3.org/TR/trace-context/)

function randomHex(bytes) {
  return Array.from(crypto.getRandomValues(new Uint8Array(bytes)), b => b.toString(16).padStart(2, '0')).join('')
}

export function traceparent() {
  return `00-${randomHex(16)}-${randomHex(8)}-01`
}
