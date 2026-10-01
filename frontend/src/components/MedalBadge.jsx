function MedalBadge({ medal }) {
  const config = {
    G: { label: 'Gold',   className: 'medal-gold' },
    S: { label: 'Silver', className: 'medal-silver' },
    B: { label: 'Bronze', className: 'medal-bronze' },
  }
  const m = config[medal]
  if (!m) return null
  return <span className={`medal-badge ${m.className}`}>{m.label}</span>
}

export default MedalBadge
