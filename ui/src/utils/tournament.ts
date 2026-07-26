/**
 * Converts a tournament slug into a human-readable display format.
 * e.g. "lcs_split_1_2026" -> "LCS SPLIT 1 2026"
 */
export function formatTournamentSlug(slug: string): string {
  return slug.split('_').join(' ').toUpperCase()
}

/**
 * Returns true if a tournament is currently active (start_date <= today <= end_date)
 * or upcoming (start_date > today), based on its date range. Returns false for
 * completed tournaments (end_date < today).
 */
export function isActiveOrUpcoming(tournament: { start_date: string; end_date: string }): boolean {
  const today = new Date().toISOString().slice(0, 10)
  return tournament.end_date >= today
}
