reset
set autoscale
set datafile separator ","
set title "Face Detection times for different image sizes"
set xlabel "Size(MB)"
set ylabel "Time(s)"
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 12
set size 1, 0.9
set output "../plot_outputs/fig_res-V-time_feat-1.eps"
plot "../compiled_data/test_output.txt" using 1:5 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:6 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:7 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:8 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:9 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:10 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:11 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:12 title col with linespoints, \
	"../compiled_data/test_output.txt" using 1:13 title col with linespoints
#set terminal png size 2560,1920 enhanced font 'NimbusSanL-Regu' 14
#set output "../plot_outputs/fig_faces-V-time_feat-3.png"
#replot