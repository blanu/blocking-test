library(arm)
library(coda)
res1 = read.coda("obfsproxy/CODAchain1.txt", "obfsproxy/CODAindex.txt")
res2 = read.coda("SSL/CODAchain1.txt", "SSL/CODAindex.txt")

dev=function(a, b) { sum((a-b)^2) }

devs=c()
for(i in seq(1,nrow(res1),100))
{
  devs=c(devs, dev(res1[i,], res1[i+1,]))
}
show(round(log(mean(devs))))

devs2=c()
for(i in seq(1,nrow(res2),100))
{
  devs2=c(devs2, dev(res2[i,], res2[i+1,]))
}
show(round(log(mean(devs2))))

devs3=c()
for(i in seq(1,nrow(res1),10))
{
  for(j in seq(1,nrow(res2),10))
  {
    devs3=c(devs3, dev(res1[i,], res2[j,]))
  }
}
show(round(log(mean(devs3))))
