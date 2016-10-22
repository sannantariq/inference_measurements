reset
set xlabel "Pixels"
set ylabel "Time(s)"
#set logscale x
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 14
set size 0.6,0.5
set output "2-RPIs-ResVTime.eps"
plot "plot_faces_res-2_pi.txt" with linespoints
set logscale x
set output "2-RPIs-ResVTime-logscale.eps"
replot
