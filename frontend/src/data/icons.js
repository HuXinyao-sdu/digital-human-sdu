export const paths = {
  arrow: '<path d="M4 12h15M13 5l7 7-7 7"/>',
  diagonal: '<path d="M6 18 18 6M6 6h12v12"/>',
  play: '<path d="m9 5 11 7-11 7Z"/>',
  pause: '<path d="M8 5v14M16 5v14"/>',
  book: '<path d="M12 5v15M12 5C8 2 3 3 3 3v15s5-1 9 2c4-3 9-2 9-2V3s-5-1-9 2Z"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="1"/><circle cx="8" cy="8" r="1.5"/><path d="m3 17 6-6 4 4 3-3 5 5"/>',
  chat: '<path d="M21 11a8 8 0 0 1-8 8H7l-4 3V5a3 3 0 0 1 3-3h7a8 8 0 0 1 8 9Z"/><path d="M7 8h10M7 12h7"/>',
  feather: '<path d="M4 21 16 9M8 17C2 7 15 0 21 3c1 8-4 17-13 14ZM8 17h7"/>',
  search: '<circle cx="10" cy="10" r="6.5"/><path d="m15 15 6 6"/>',
  close: '<path d="m6 6 12 12M6 18 18 6"/>',
  back: '<path d="M20 12H5M11 5l-7 7 7 7"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  volume: '<path d="m11 4-5 5H2v6h4l5 5ZM15 8a6 6 0 0 1 0 8M18 4a11 11 0 0 1 0 16"/>',
  mute: '<path d="m11 4-5 5H2v6h4l5 5ZM16 9l6 6M22 9l-6 6"/>',
  reset: '<path d="M3 10a9 9 0 1 1 1 8M3 3v7h7"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  pin: '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
  chevron: '<path d="m8 4 8 8-8 8"/>',
  heart: '<path d="M20 5c-3-3-6-1-8 1-2-2-5-4-8-1-5 5 5 12 8 15 3-3 13-10 8-15Z"/>',
  sparkle: '<path d="m12 2 2.5 7.5L22 12l-7.5 2.5L12 22l-2.5-7.5L2 12l7.5-2.5Z"/>'
}
export const icon = (name, cls = '') => `<svg class="icon ${cls}" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.arrow}</svg>`
