reset
set xlabel "Extra Facial Features"
set ylabel "Time(s)"
#set logscale x
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 14
set size 0.6,0.5
set output "FeatVsTime.eps"
plot "plot_multi_feat.txt" with linespoints
set logscale x
set output "FeatVsTime-logscale.eps"
replot
