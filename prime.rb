puts "Enter a number:"
num = gets.to_i

is_prime = true

if num <= 1
  is_prime = false
else
  (2..Math.sqrt(num)).each do |i|
    if num % i == 0
      is_prime = false
      break
    end
  end
end

if is_prime
  puts "#{num} is a Prime Number"
else
  puts "#{num} is Not a Prime Number"
end