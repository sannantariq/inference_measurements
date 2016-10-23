reset
set autoscale
set title "Face Detection times for different image sizes"
set xlabel "Size"
set ylabel "Time(s)"
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 14
set size 0.6,0.5
set output "../plot_outputs/fig_res-V-time_feat-1.eps"
plot "../raw_data/output_res-V-time_feat-1.txt" using 1:2 title col with linespoints, \
	"../raw_data/output_res-V-time_feat-1.txt" using 1:3 title col with linespoints, \
	"../raw_data/output_res-V-time_feat-1.txt" using 1:4 title col with linespoints;
set output "../plot_outputs/fig_res-V-time_feat-1.png"
replot