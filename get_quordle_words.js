const excludedWords = new Set([
  "gypsy",
  "gipsy",
  "mammy",
  "agora",
  "slave",
  "hussy",
]);

const words = require("./quordle_list.json");

const RandomEngine = function (e) {
  e == null && (e = new Date().getTime()),
    (this.N = 624),
    (this.M = 397),
    (this.MATRIX_A = 2567483615),
    (this.UPPER_MASK = 2147483648),
    (this.LOWER_MASK = 2147483647),
    (this.mt = new Array(this.N)),
    (this.mti = this.N + 1),
    e.constructor == Array
      ? this.init_by_array(e, e.length)
      : this.init_seed(e);
};
RandomEngine.prototype.init_seed = function (e) {
  for (this.mt[0] = e >>> 0, this.mti = 1; this.mti < this.N; this.mti++) {
    var e = this.mt[this.mti - 1] ^ (this.mt[this.mti - 1] >>> 30);
    (this.mt[this.mti] =
      ((((e & 4294901760) >>> 16) * 1812433253) << 16) +
      (e & 65535) * 1812433253 +
      this.mti),
      (this.mt[this.mti] >>>= 0);
  }
};
RandomEngine.prototype.random_int = function () {
  var e,
    t = new Array(0, this.MATRIX_A);
  if (this.mti >= this.N) {
    var n;
    for (
      this.mti == this.N + 1 && this.init_seed(5489), n = 0;
      n < this.N - this.M;
      n++
    )
      (e = (this.mt[n] & this.UPPER_MASK) | (this.mt[n + 1] & this.LOWER_MASK)),
        (this.mt[n] = this.mt[n + this.M] ^ (e >>> 1) ^ t[e & 1]);
    for (; n < this.N - 1; n++)
      (e = (this.mt[n] & this.UPPER_MASK) | (this.mt[n + 1] & this.LOWER_MASK)),
        (this.mt[n] = this.mt[n + (this.M - this.N)] ^ (e >>> 1) ^ t[e & 1]);
    (e =
      (this.mt[this.N - 1] & this.UPPER_MASK) | (this.mt[0] & this.LOWER_MASK)),
      (this.mt[this.N - 1] = this.mt[this.M - 1] ^ (e >>> 1) ^ t[e & 1]),
      (this.mti = 0);
  }
  return (
    (e = this.mt[this.mti++]),
    (e ^= e >>> 11),
    (e ^= (e << 7) & 2636928640),
    (e ^= (e << 15) & 4022730752),
    (e ^= e >>> 18),
    e >>> 0
  );
};
RandomEngine.prototype.random_int31 = function () {
  return this.random_int() >>> 1;
};

const getWords = (e) => {
  let wordSet;
  const t = new RandomEngine(e);
  t.random_int31(), t.random_int31(), t.random_int31(), t.random_int31();
  do
    wordSet = [
      words[t.random_int31() % words.length],
      words[t.random_int31() % words.length],
      words[t.random_int31() % words.length],
      words[t.random_int31() % words.length],
    ];
  while (
    wordSet[0] === wordSet[1] ||
    wordSet[0] === wordSet[2] ||
    wordSet[0] === wordSet[3] ||
    wordSet[1] === wordSet[2] ||
    wordSet[1] === wordSet[3] ||
    wordSet[2] === wordSet[3] ||
    excludedWords.has(wordSet[0]) ||
    excludedWords.has(wordSet[1]) ||
    excludedWords.has(wordSet[2]) ||
    excludedWords.has(wordSet[3])
  );
  return wordSet;
};

const getEndDate = () => {
  const date = new Date();
  try {
    const args = process.argv.slice(2);
    const dateOffset = args[0];
    if (dateOffset) date.setDate(date.getDate() + parseInt(dateOffset));
  } finally {
    return date;
  }
};

const startDate = new Date("01/24/2022");
const endDate = getEndDate();
const millisecondsPerDay = 24 * 60 * 60 * 1e3;
const seed =
  ((endDate.getTime() - startDate.getTime()) / millisecondsPerDay) >> 0;

const quordleToday = getWords(seed);
console.log(JSON.stringify(quordleToday));
