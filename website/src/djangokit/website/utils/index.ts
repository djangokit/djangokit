/**
 * Generate a range of numbers.
 *
 * @param quantity
 * @param start
 */
export function* range(quantity, start = 0) {
  const end = start + quantity;
  for (let i = start; i < end; ++i) {
    yield i;
  }
}
