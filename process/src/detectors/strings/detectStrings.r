library(arm)
library(coda)
library('plyr')

dev=function(a, b) { sum((a-b)^2) }
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

res1 = read.coda("obfsproxy/CODAchain1.txt", "obfsproxy/CODAindex.txt")
res2 = read.coda("SSL/CODAchain1.txt", "SSL/CODAindex.txt")

files=read.csv('files.csv', header=FALSE)

for(file in files$V1)
{
  print(file)
  lengths=read.csv(file, header=FALSE)
  data=mkdata(lengths)

  devs=c()
  for(i in seq(1,nrow(res1)))
  {
    devs=c(devs, dev(data, res1[i,]))
  }
  d1=log(mean(devs))

  devs2=c()
  for(i in seq(1,nrow(res2)))
  {
    devs2=c(devs2, dev(data, res2[i,]))
  }
  d2=log(mean(devs2))

  show(c(d1, d2))

  if(d1<d2)
  {
    print('obfsproxy')
  }
  else if(d1>d2)
  {
    print('SSL')
  }
  else
  {
    print('Undecided')
  }
}