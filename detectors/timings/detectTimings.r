library(arm)
library(coda)
library('plyr')

dev=function(a, b) { sum((a-b)^2) }

res1 = read.coda("obfsproxy/CODAchain1.txt", "obfsproxy/CODAindex.txt")
res2 = read.coda("SSL/CODAchain1.txt", "SSL/CODAindex.txt")

files=read.csv('files.csv', header=FALSE)
files=files$V1
d1s=c()
d2s=c()
decisions=c()

for(file in files)
{
  print(file)
  timings=read.csv(file, header=FALSE)
  data=round(timings$V1*1000)
  print(data)

  size=min(length(data), length(res1))
  d1=dev(data[1:size], res1[1:size])
  d1s=c(d1s, d1)

  devs2=c()
  size=min(length(data), length(res2))
  d2=dev(data[1:size], res2[1:size])
  d2s=c(d2s, d2)

  show(c(d1, d2))

  if(d1<d2)
  {
    print('obfsproxy')
    decisions=c(decisions, 'obfsproxy')
  }
  else if(d1>d2)
  {
    print('SSL')
    decisions=c(decisions, 'SSL')
  }
  else
  {
    print('Undecided')
    decisions=c(decisions, 'Undecided')
  }
}

frame=data.frame(file=files, d1=d1s, d2=d2s, decision=decisions)
write.csv(frame, file='output.csv')
