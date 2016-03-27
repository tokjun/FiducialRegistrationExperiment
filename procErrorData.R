library(ggplot2)


plot.with.error.bar <- function(x, y, sd, ymin, ymax) {
    plot(x, y, ylim=c(ymin, ymax))
    segments(x, y-sd, x, y+sd)
    epsilon <- 5
    segments(x-epsilon, y-sd, x+epsilon,y-sd)
    segments(x-epsilon, y+sd, x+epsilon,y+sd)
}

plot.errors <- function(r, ymin, ymax, title) {
    p <- ggplot(r, aes(x=x, y=mean, group=Direction, color=Direction)) + geom_line() + geom_point() + labs(title=title, x="Translation (mm)", y = "Error (mm)") + theme_classic() + scale_color_manual(values=c('#FFA0A0','#A0FFA0', '#A0A0FF'))
    print(p)
}

plot.errors.error.bars <- function(r, ymin, ymax, title) {
    p <- ggplot(r, aes(x=x, y=mean, group=Direction, color=Direction)) + geom_line() + geom_point() + geom_errorbar(aes(ymin=r$mean-r$sd, ymax=r$mean+r$sd), width=2,position=position_dodge(0.5)) + labs(title=title, x="Translation (mm)", y = "Error (mm)") + theme_classic() + scale_color_manual(values=c('#FFA0A0','#A0FFA0', '#A0A0FF'))
    print(p)
}

aggregate.errors.x <- function(x, by) {
    m <- aggregate(x, list(by), mean)
    s <- aggregate(x, list(by), sd)
    r <- data.frame(x=m$Group.1, mean=m$x, sd=s$x)
    return (r)
}

aggregate.errors.all <- function(data, by, dirName) {
    r <- c()
    r$dR <- aggregate.errors.x(data$dR, data[[by]])
    r$dR$Direction <- dirName
    r$dA <- aggregate.errors.x(data$dA, data[[by]])
    r$dA$Direction <- dirName
    r$dS <- aggregate.errors.x(data$dS, data[[by]])
    r$dS$Direction <- dirName
    
    r$ThetaR <- aggregate.errors.x(data$ThetaR, data[[by]])
    r$ThetaR$Direction <- dirName
    r$ThetaA <- aggregate.errors.x(data$ThetaA, data[[by]])
    r$ThetaA$Direction <- dirName
    r$ThetaS <- aggregate.errors.x(data$ThetaS, data[[by]])
    r$ThetaS$Direction <- dirName
    
    sqre <- data$dR^2 + data$dA^2 + data$dS^2
    r$RMS <- aggregate.errors.x(sqre, data[[by]])
    r$RMS$mean <- sqrt(r$RMS$mean)
    r$RMS$sd <- sqrt(r$RMS$sd)
    r$RMS$Direction <- dirName
    return (r)
}


setwd('/home/develop/Projects/Canon/FiducialTest')
errorData1119 <- read.csv('Error-2015-11-19.csv')
errorData1119$date <- 1119

errorData1127 <- read.csv('Error-2015-11-27.csv')
errorData1127$date <- 1127

errorData1204 <- read.csv('Error-2015-12-04.csv')
errorData1204$date <- 1204

errorData1210 <- read.csv('Error-2015-12-10.csv')
errorData1210$date <- 1210

errorData <- rbind(errorData1119, errorData1127, errorData1204, errorData1210)

# Plot R, A, and S errors vs R-translation
errorData$R <- (-errorData$R)
errorData$S <- (-errorData$S)

tmin <- -8
tmax <- 8

trans <- errorData[errorData$BlockTilt==0&errorData$BlockRot==0&errorData$FiducialRot==0,]
transR <- trans[trans$A==10&trans$S==0,]
tR <- aggregate.errors.all(transR, "R", "R")
transA <- trans[trans$R==0&trans$S==0,]
tA <- aggregate.errors.all(transA, "A", "A")
transS <- trans[trans$R==0&trans$A==10,]
tS <- aggregate.errors.all(transS, "S", "S")

transRMS <- rbind(tR$RMS, tA$RMS, tS$RMS)  # Exclude AP direction
pdf("trans-RMS.pdf")
plot.errors(transRMS, tmin, tmax, 'Root Mean Square Errors')
dev.off()

##BlockRot=0 : facing door of MR room
rot <- errorData[errorData$R==0&errorData$A==10&errorData$S==0,]
rotR <- rot[errorData$BlockRot==0&errorData$FiducialRot==0,]
rR <- aggregate.errors.all(rotR, "BlockTilt", "RotR")
rotS <- rot[errorData$BlockRot==90&errorData$FiducialRot==0,]
rS <- aggregate.errors.all(rotS, "BlockTilt", "RotS")
rotA <- rot[errorData$BlockRot==0,]
rA <- aggregate.errors.all(rotA, "FiducialRot", "RotA")

rotRMS <- rbind(rR$RMS, rS$RMS, rA$RMS)  # Exclude AP direction
pdf("rot-RMS.pdf")
plot.errors(rotRMS, tmin, tmax, 'Root Mean Square Errors')
dev.off()

