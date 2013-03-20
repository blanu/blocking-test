library('ProjectTemplate')
load.project()

jags <- jags.model('multinomial.bug',
                   data = list('lengths' = data,
                               'N' = N,
                               'K' = K),
                   n.chains = 1)

mcmc.samples <- coda.samples(jags,
                             c('p'),
                             1000)

# Estimate the model parameters using our samples.
credible.intervals <- data.frame()

for (i in 1:K)
{
  estimated.values <- as.array(mcmc.samples[,paste('p[', i, ']', sep = ''),])
  credible.interval <- as.numeric(quantile(estimated.values,
                                           prob = c(0.025, 0.975)))
  credible.intervals <- rbind(credible.intervals,
                              data.frame(Type = data[i],
                                         Median = median(estimated.values),
                                         LowerBound = credible.interval[1],
                                         UpperBound = credible.interval[2]))
}

# Visualize the parameters.
png(file.path('graphs', 'lengths.png'))
p <- ggplot(credible.intervals, aes(x = reorder(Type, Median), y = Median)) +
  geom_point() +
  geom_pointrange(aes(ymin = LowerBound, ymax = UpperBound)) +
  coord_flip() +
  ylim(c(0, 1)) +
  scale_y_log10() +
  ylab('') +
  opts(title = 'Lengths') +
  xlab('')
print(p)
dev.off()
