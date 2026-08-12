export class SeededRng {
  constructor(seed) { this.state = Number(seed) >>> 0; }
  next() { let value = this.state += 0x6D2B79F5; value = Math.imul(value ^ value >>> 15, value | 1); value ^= value + Math.imul(value ^ value >>> 7, value | 61); return ((value ^ value >>> 14) >>> 0) / 4294967296; }
  int(min, max) { return Math.floor(this.next() * (max - min + 1)) + min; }
  pick(items) { return items[this.int(0, items.length - 1)]; }
  shuffle(items) { const result = [...items]; for (let index = result.length - 1; index > 0; index -= 1) { const other = this.int(0, index); [result[index], result[other]] = [result[other], result[index]]; } return result; }
}
