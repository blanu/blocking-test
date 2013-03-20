library('plyr')

strings=read.csv('strings.csv', header=FALSE)

N = length(strings$V1)
K = max(strings$V1)
data=rep(1,K)
for(i in seq(1,nrow(strings)))
{
  data[strings[i,1]]=strings[i,2]+1
}

cat('N <-', N, "\n", file='data.txt')
cat('K <-', K, "\n", file='data.txt', append=TRUE)
cat('strings <- c(', paste(data, collapse=','), ")\n", file='data.txt', append=TRUE)
