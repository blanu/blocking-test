library(coda)
library('plyr')

res1 = read.table('obfsproxy.csv', sep=',')
#res1 = read.coda("obfsproxy/CODAchain1.txt", "obfsproxy/CODAindex.txt")
res2 = read.table('SSL.csv', sep=',')
#res2 = read.coda("SSL/CODAchain1.txt", "SSL/CODAindex.txt")
res3 = read.table('Dust.csv', sep=',')
#res3 = read.coda("Dust/CODAchain1.txt", "Dust/CODAindex.txt")

file='../../traces/test2/tagged/obfsproxy/tcp_69.93.61.234_1051_192.168.137.43_53846.length'
print(file)
data=read.table(file=file)

mkdata=function(lengths)
{
  K = max(c(1500, max(lengths$V1)))
  data=rep(1,K)
  freq=count(lengths$V1)
  for(i in seq(1,nrow(freq)))
  {
    data[freq[i,1]]=freq[i,2]+1
  }

  data
}

d=mkdata(data)
print(sum(d))
print(sum(abs(d-res1[1,])))
print(sum(abs(d-res2[1,])))
print(sum(abs(d-res3[1,])))
