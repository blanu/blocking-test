library('plyr')

entropy=read.csv('entropy.csv', header=FALSE)

N = length(entropy$V1)

cat('N <-', N, "\n", file='data.txt')
cat('entropy <- c(', file='data.txt', append=TRUE)
data=paste(entropy$V1, collapse=',')
cat(data, file='data.txt', append=TRUE)
cat(")\n", file='data.txt', append=TRUE)
