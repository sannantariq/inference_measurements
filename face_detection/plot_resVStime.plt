reset
set xlabel "Resolution(pixels)"
set ylabel "Time(s)"
#set logscale x
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 14
set size 0.6,0.5
set output "ResVsTime.eps"
plot "plot.txt" with linespoints
set logscale x
set output "ResVsTime-logscale.eps"
replot
