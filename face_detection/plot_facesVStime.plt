reset
set xlabel "Faces"
set ylabel "Time(s)"
#set logscale x
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 14
set size 0.6,0.5
set output "2-RPIs-FacesVsTime.eps"
plot "plot_multi_2-rpi.txt" with linespoints
set logscale x
set output "2-RPIs-FacesVsTime-logscale.eps"
replot
