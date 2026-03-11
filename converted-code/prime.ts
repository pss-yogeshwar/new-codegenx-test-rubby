typescript
const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});

readline.question('Enter a number: ', (num) => {
  const numValue = parseInt(num);

  let isPrime = true;

  if (numValue <= 1) {
    isPrime = false;
  } else {
    for (let i = 2; i <= Math.sqrt(numValue); i++) {
      if (numValue % i === 0) {
        isPrime = false;
        break;
      }
    }
  }

  if (isPrime) {
    console.log(`${numValue} is a Prime Number`);
  } else {
    console.log(`${numValue} is Not a Prime Number`);
  }

  readline.close();
});