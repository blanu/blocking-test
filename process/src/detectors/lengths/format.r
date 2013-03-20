library('plyr')

lengths=read.csv('lengths.csv', header=FALSE)

N = length(lengths$V1)
K = max(c(1500, max(lengths$V1)))
data=rep(1,K)
freq=count(lengths$V1)
for(i in seq(1,nrow(freq)))
{
  data[freq[i,1]]=freq[i,2]+1
}

cat('N <-', N, "\n", file='data.txt')
cat('K <-', K, "\n", file='data.txt', append=TRUE)
cat('lengths <- c(', paste(data, collapse=','), ")\n", file='data.txt', append=TRUE)
