library(coda)

res1 = read.coda("obfsproxy/CODAchain1.txt", "obfsproxy/CODAindex.txt")
res2 = read.coda("SSL/CODAchain1.txt", "SSL/CODAindex.txt")
res3 = read.coda("Dust/CODAchain1.txt", "Dust/CODAindex.txt")

files=read.csv('files.csv', header=FALSE)
files=files$V1

d1s=c()
d2s=c()
d3s=c()
answers=c()
decisions=c()
corrects=c()
labels=c('obfsproxy', 'SSL', 'Dust')

for(file in files)
{
  entropy=read.csv(file, header=FALSE)
  data=entropy$V1

  d1=dnorm(data, mean(res1[,1]), mean(res1[,2]))
  d2=dnorm(data, mean(res2[,1]), mean(res2[,2]))
  d3=dnorm(data, mean(res3[,1]), mean(res3[,2]))
  d1s=c(d1s, d1)
  d2s=c(d2s, d2)
  d3s=c(d3s, d3)

  ds=c(d1,d2,d3)
  md=max(ds)
  di=which(ds==md)
  decision=labels[di]

  decisions=c(decisions, decision)
}

frame=data.frame(file=files, d1=d1s, d2=d2s, d3=d3s, decision=decisions)
write.table(frame, file='output.csv', col.names=FALSE, row.names=FALSE, sep=",")
