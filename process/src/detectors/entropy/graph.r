library(coda)

res1 = read.coda("obfsproxy/CODAchain1.txt", "obfsproxy/CODAindex.txt")
res2 = read.coda("SSL/CODAchain1.txt", "SSL/CODAindex.txt")
res3 = read.coda("Dust/CODAchain1.txt", "Dust/CODAindex.txt")

print(res1[,2])

x=seq(0,99)
d1=dnorm(x, mean(res1[,1]), mean(res1[,2]))
d2=dnorm(x, mean(res2[,1]), mean(res2[,2]))
d3=dnorm(x, mean(res3[,1]), mean(res3[,2]))

plot(x, d3, col=3, type='l')
lines(x, d1, col=1)
lines(x, d2, col=2)

print(mean(d1))
print(mean(d2))
print(mean(d3))
